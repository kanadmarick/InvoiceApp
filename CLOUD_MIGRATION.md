# Cloud Migration Guide — Oracle Cloud Infrastructure (OCI)

> **Complete step-by-step copy-paste instructions** for deploying the Django Invoice App  
> to an Oracle Cloud Always Free Tier VM (Ubuntu 22.04).  
> Last deployed: **March 10, 2026** at `152.70.79.182`

---

## Table of Contents

1. [Prerequisites & What You Need](#1-prerequisites--what-you-need)
2. [Create the OCI VM Instance](#2-create-the-oci-vm-instance)
3. [OCI Security List — Open Ports 80 & 443](#3-oci-security-list--open-ports-80--443)
4. [SSH Into the VM](#4-ssh-into-the-vm)
5. [Run the Server Setup Script](#5-run-the-server-setup-script)
6. [Clone the Repository](#6-clone-the-repository)
7. [Configure Environment Variables](#7-configure-environment-variables)
8. [Build & Launch Containers](#8-build--launch-containers)
9. [Create Users & Load Demo Data](#9-create-users--load-demo-data)
10. [Verify the Deployment](#10-verify-the-deployment)
11. [Enable HTTPS with Let's Encrypt (Optional)](#11-enable-https-with-lets-encrypt-optional)
12. [Maintenance & Operations](#12-maintenance--operations)
13. [Troubleshooting](#13-troubleshooting)
14. [Architecture Overview](#14-architecture-overview)

---

## 1. Prerequisites & What You Need

| Item | Details |
|------|---------|
| **OCI Account** | Free tier at [cloud.oracle.com](https://cloud.oracle.com) |
| **SSH Key Pair** | Generated during VM creation (e.g., `ssh-key-2026-03-02.key`) |
| **Git Repo** | `https://github.com/kanadmarick/InvoiceApp.git` |
| **Local Tools** | Git Bash (Windows) or any terminal with SSH |
| **VM Specs Used** | AMD x86_64, Ubuntu 22.04, 1 OCPU, 1 GB RAM, 47 GB disk |

### Set SSH Key Variable (run once per terminal session)

```bash
# Windows Git Bash
export SSH_KEY="/c/Users/kanad/Downloads/ssh-key-2026-03-02.key"

# Linux / macOS
export SSH_KEY="$HOME/Downloads/ssh-key-2026-03-02.key"
```

### Fix SSH Key Permissions (first time only)

```bash
chmod 600 "$SSH_KEY"
```

---

## 2. Create the OCI VM Instance

1. Log into [OCI Console](https://cloud.oracle.com) → **Compute** → **Instances** → **Create Instance**
2. **Image:** Ubuntu 22.04 (Canonical)
3. **Shape:** VM.Standard.E2.1.Micro (Always Free) — AMD x86_64
   - Or VM.Standard.A1.Flex (ARM Ampere A1, up to 4 OCPU / 24 GB RAM — also Always Free)
4. **Networking:** Use default VCN or create one with a public subnet
5. **SSH Keys:** Upload your public key (or let OCI generate a pair — download the `.key`)
6. **Boot volume:** Default 47 GB is sufficient
7. Click **Create** and note the **Public IP address** (e.g., `152.70.79.182`)

---

## 3. OCI Security List — Open Ports 80 & 443

OCI blocks ports 80/443 by default in the **VCN Security List** (separate from iptables).

1. Go to **Networking** → **Virtual Cloud Networks** → click your VCN
2. Click the **Public Subnet** → click the **Default Security List**
3. Click **Add Ingress Rules** and add:

| Source CIDR | Protocol | Dest Port | Description |
|-------------|----------|-----------|-------------|
| `0.0.0.0/0` | TCP | 80 | HTTP |
| `0.0.0.0/0` | TCP | 443 | HTTPS |

> **This is critical.** Without these rules, the VM won't be reachable on ports 80/443 even if iptables is open.

---

## 4. SSH Into the VM

```bash
ssh -i "$SSH_KEY" ubuntu@152.70.79.182
```

Verify you're in:

```bash
uname -a
# Expected: Linux ... x86_64 ... Ubuntu ...
```

---

## 5. Run the Server Setup Script

### Option A: Copy from repo (if already cloned)

```bash
# On the VM
bash /opt/invoices/server-setup.sh
```

### Option B: Run from local machine via SSH

```bash
# From your local terminal
scp -i "$SSH_KEY" server-setup.sh ubuntu@152.70.79.182:/tmp/
ssh -i "$SSH_KEY" ubuntu@152.70.79.182 'bash /tmp/server-setup.sh'
```

### What the script does:

1. `apt update && upgrade` — System updates
2. Installs **Docker** + **Docker Compose plugin**
3. Adds `ubuntu` user to `docker` group
4. Installs **git**, **fail2ban** (SSH brute-force protection)
5. Opens **iptables** ports 80 & 443 (OCI Ubuntu uses iptables, not ufw)
6. Installs **iptables-persistent** to survive reboots
7. Creates `/opt/invoices` directory
8. Enables **unattended-upgrades** for auto security patches
9. Creates **cron job** for SSL cert renewal (certbot)

### IMPORTANT: Log out and back in after setup

```bash
exit
ssh -i "$SSH_KEY" ubuntu@152.70.79.182
```

This activates the `docker` group membership (otherwise you get "permission denied").

### Verify Docker is working:

```bash
docker --version
# Docker version 29.2.1, build ...

docker compose version
# Docker Compose version v2.x.x
```

### If iptables rules didn't persist, re-run manually:

```bash
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save
```

---

## 6. Clone the Repository

```bash
cd /opt/invoices
git clone https://github.com/kanadmarick/InvoiceApp.git .
```

> The `.` clones directly into `/opt/invoices` (not a subfolder).

If the directory isn't empty:

```bash
sudo rm -rf /opt/invoices/*
sudo rm -rf /opt/invoices/.*  2>/dev/null
git clone https://github.com/kanadmarick/InvoiceApp.git .
```

Verify:

```bash
ls -la
# Should show: docker-compose.prod.yml, Dockerfile.prod, manage.py, nginx/, etc.
```

---

## 7. Configure Environment Variables

### Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Create .env.prod from the example:

```bash
cp .env.prod.example .env.prod
```

### Edit with your values:

```bash
nano .env.prod
```

### Or do it all in one shot (copy-paste ready):

```bash
cd /opt/invoices

# Generate a random secret key
RANDOM_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Create and configure .env.prod
cp .env.prod.example .env.prod
sed -i "s|change-me-to-a-real-secret-key|$RANDOM_KEY|" .env.prod
sed -i "s|YOUR_DOMAIN,152.70.79.182|152.70.79.182|" .env.prod
sed -i "s|change-me-to-a-strong-password|YourStrongDbPassword123|g" .env.prod
sed -i "s|https://YOUR_DOMAIN|http://152.70.79.182|g" .env.prod
sed -i "s|change-me-guest-password|YourGuestPassword123|" .env.prod

# Verify
cat .env.prod
```

### What the final .env.prod should look like:

```dotenv
SECRET_KEY=<random-64-char-token>
DEBUG=False
ALLOWED_HOSTS=152.70.79.182

POSTGRES_DB=invoices
POSTGRES_USER=invoices
POSTGRES_PASSWORD=YourStrongDbPassword123

DB_ENGINE=django.db.backends.postgresql
DB_NAME=invoices
DB_USER=invoices
DB_PASSWORD=YourStrongDbPassword123
DB_HOST=db
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://152.70.79.182
CSRF_TRUSTED_ORIGINS=http://152.70.79.182

SECURE_SSL_REDIRECT=False

GUEST_USERNAME=guest
GUEST_PASSWORD=YourGuestPassword123
```

> **Note:** `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` use `http://` (not https) because  
> we start without SSL. Change to `https://yourdomain.com` after enabling SSL.

---

## 8. Build & Launch Containers

### If the host has nginx installed (conflicts with port 80):

```bash
sudo systemctl stop nginx
sudo systemctl disable nginx
```

### Build and start everything:

```bash
cd /opt/invoices
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

This builds two images and starts 3 services:

| Service | Container | What It Does |
|---------|-----------|-------------|
| **db** | `invoices_db` | PostgreSQL 15 Alpine — database |
| **web** | `invoices_web` | Django + Gunicorn — API backend (runs migrations on startup) |
| **nginx** | `invoices_nginx` | Nginx + React SPA — serves frontend & proxies API |
| **certbot** | `invoices_certbot` | Exits immediately until you request an SSL cert |

> **Build time:** ~5–10 minutes on first run (Playwright Chromium download is ~300 MB).  
> Subsequent builds use Docker cache and take seconds.

### If `up -d --build` gives issues, build individually:

```bash
# Build web image (Django + Gunicorn + Playwright)
docker compose -f docker-compose.prod.yml --env-file .env.prod build web

# Build nginx image (React SPA + Nginx reverse proxy)
docker compose -f docker-compose.prod.yml --env-file .env.prod build nginx

# Start all services
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

### Verify all containers are running:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

**Expected output:**

```
NAMES              STATUS                   PORTS
invoices_nginx     Up X minutes             0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
invoices_web       Up X minutes             8000/tcp
invoices_db        Up X minutes (healthy)   5432/tcp
```

### If nginx is "Restarting" — check logs:

```bash
docker compose -f docker-compose.prod.yml logs nginx --tail=20
```

Common fix: if nginx was created during a port conflict (host nginx was running), the container  
may not have the correct network. Recreate it:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod stop nginx
docker compose -f docker-compose.prod.yml --env-file .env.prod rm -f nginx
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d nginx
```

### Check web container logs (migrations + Gunicorn):

```bash
docker compose -f docker-compose.prod.yml logs web --tail=40
```

**Expected:** All migrations applied → "Listening at: http://0.0.0.0:8000" → 3 workers booted.

---

## 9. Create Users & Load Demo Data

### Create admin superuser:

```bash
# Create superuser (no password set yet)
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser \
    --noinput --username admin --email admin@example.com

# Set the admin password
docker compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.get(username='admin')
u.set_password('YourAdminPassword123')
u.save()
print('Admin password set')
"
```

### Create guest demo user:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username='guest')
u.set_password('YourGuestPassword123')
u.save()
print('Guest user', 'created' if created else 'updated')
"
```

> **Important:** The guest password here must match `GUEST_PASSWORD` in `.env.prod`  
> (used by the one-click "Guest Login" button on the React frontend).

### Load demo data (30 invoices, 3 businesses):

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py populate_dummy_data
```

---

## 10. Verify the Deployment

### From your local machine:

```bash
# React SPA (should return 200)
curl -s -o /dev/null -w '%{http_code}' http://152.70.79.182/

# Swagger API Docs (should return 200)
curl -s -o /dev/null -w '%{http_code}' http://152.70.79.182/api/docs/

# Django Admin (should return 200)
curl -s -o /dev/null -w '%{http_code}' http://152.70.79.182/admin/login/
```

### Open in a browser:

| What | URL |
|------|-----|
| **React Frontend** | http://152.70.79.182 |
| **Swagger API Docs** | http://152.70.79.182/api/docs/ |
| **Django Admin Panel** | http://152.70.79.182/admin/ |

### Test the API with JWT auth:

```bash
# Get JWT tokens
curl -s -X POST http://152.70.79.182/accounts/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"YourAdminPassword123"}' | python3 -m json.tool

# Use the access token to hit a protected endpoint
curl -s http://152.70.79.182/billings/invoices/ \
  -H "Authorization: Bearer <access_token_here>" | python3 -m json.tool
```

---

## 11. Enable HTTPS with Let's Encrypt (Optional)

> **Requires a domain name.** Let's Encrypt cannot issue certificates for bare IP addresses.

### Step 1: Point your domain to the VM

Create a DNS **A record** pointing your domain to `152.70.79.182`:

```
invoices.yourdomain.com  →  A  →  152.70.79.182
```

Wait for DNS propagation (check with `dig invoices.yourdomain.com`).

### Step 2: Update ALLOWED_HOSTS in .env.prod

```bash
nano .env.prod
```

Change:

```dotenv
ALLOWED_HOSTS=invoices.yourdomain.com,152.70.79.182
CORS_ALLOWED_ORIGINS=https://invoices.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://invoices.yourdomain.com
SECURE_SSL_REDIRECT=True
```

### Step 3: Obtain the SSL certificate

```bash
cd /opt/invoices

docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d invoices.yourdomain.com \
  --email your-email@gmail.com \
  --agree-tos --no-eff-email
```

### Step 4: Switch nginx to the SSL config

```bash
cd /opt/invoices

# Replace YOUR_DOMAIN in the SSL config with your actual domain
sed 's/YOUR_DOMAIN/invoices.yourdomain.com/g' nginx/default-ssl.conf > nginx/default.conf

# Rebuild and restart nginx
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build nginx

# Restart web to pick up new env vars
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d web
```

### Step 5: Verify HTTPS

```bash
curl -s -o /dev/null -w '%{http_code}' https://invoices.yourdomain.com/
# Should return 200
```

### SSL Auto-Renewal

The server setup script already created a cron job that runs daily at 3 AM:

```
0 3 * * * cd /opt/invoices && docker compose -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

Verify it's in place:

```bash
crontab -l
```

---

## 12. Maintenance & Operations

### Shorthand (set an alias for convenience)

```bash
# Add to ~/.bashrc
alias dc='cd /opt/invoices && docker compose -f docker-compose.prod.yml --env-file .env.prod'
source ~/.bashrc

# Now you can run:
dc up -d
dc logs web --tail=50
dc ps
dc down
```

### View logs

```bash
cd /opt/invoices

# All services
docker compose -f docker-compose.prod.yml logs -f --tail=50

# Specific service
docker compose -f docker-compose.prod.yml logs web --tail=100
docker compose -f docker-compose.prod.yml logs nginx --tail=100
docker compose -f docker-compose.prod.yml logs db --tail=100
```

### Deploy updates (after pushing to GitHub)

```bash
cd /opt/invoices
git pull origin main
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

### Restart all services

```bash
cd /opt/invoices
docker compose -f docker-compose.prod.yml --env-file .env.prod restart
```

### Restart a single service

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod restart web
docker compose -f docker-compose.prod.yml --env-file .env.prod restart nginx
```

### Stop everything

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod down
```

### Stop and remove all data (DESTRUCTIVE)

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod down -v
```

### Django shell access

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py shell
```

### Database shell access

```bash
docker compose -f docker-compose.prod.yml exec db psql -U invoices -d invoices
```

### Database backup

```bash
docker compose -f docker-compose.prod.yml exec db pg_dump -U invoices invoices > backup_$(date +%Y%m%d).sql
```

### Database restore

```bash
cat backup_20260310.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U invoices -d invoices
```

### Check disk usage

```bash
df -h /
docker system df
```

### Clean unused Docker resources

```bash
docker system prune -af --volumes
# WARNING: This removes ALL unused images, containers, and volumes
```

---

## 13. Troubleshooting

### Problem: Nginx container is "Restarting"

**Cause:** Usually `host not found in upstream "web:8000"` — the nginx container lost its network.

```bash
# Check the error
docker compose -f docker-compose.prod.yml logs nginx --tail=10

# Fix: recreate the container
docker compose -f docker-compose.prod.yml --env-file .env.prod stop nginx
docker compose -f docker-compose.prod.yml --env-file .env.prod rm -f nginx
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d nginx
```

### Problem: Port 80 already in use

**Cause:** Host-level nginx from a previous installation.

```bash
# Find what's using port 80
sudo ss -tlnp | grep ':80 '

# Stop and disable host nginx
sudo systemctl stop nginx
sudo systemctl disable nginx

# Then start the Docker nginx container
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d nginx
```

### Problem: Django returns "Bad Request (400)"

**Cause:** The `Host` header doesn't match `ALLOWED_HOSTS`.

```bash
# Test with correct host header
curl -H "Host: 152.70.79.182" http://localhost/api/docs/

# Fix: add the missing host to .env.prod
nano .env.prod
# ALLOWED_HOSTS=152.70.79.182,yourdomain.com

# Restart web
docker compose -f docker-compose.prod.yml --env-file .env.prod restart web
```

### Problem: Static files (admin CSS) not loading

```bash
# Re-collect static files
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Or rebuild the web container
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build web
```

### Problem: Database connection refused

```bash
# Check if db is healthy
docker ps --filter name=invoices_db

# Check db logs
docker compose -f docker-compose.prod.yml logs db --tail=30

# If db is not starting, check disk space
df -h /
```

### Problem: Can't reach the site from browser

Check all 3 layers:

```bash
# 1. Is the container running?
docker ps

# 2. Are iptables open?
sudo iptables -L INPUT -n | grep -E '80|443'

# 3. Is OCI Security List configured? (check in OCI Console)
# Networking → VCN → Subnet → Security List → must have port 80/443 ingress rules
```

### Problem: PDF generation fails

```bash
# Playwright Chromium needs to be installed in the container
docker compose -f docker-compose.prod.yml exec web playwright install chromium

# Or rebuild the web image
docker compose -f docker-compose.prod.yml --env-file .env.prod build web
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d web
```

---

## 14. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Oracle Cloud VM (Ubuntu 22.04)               │
│                     IP: 152.70.79.182                           │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                Docker Compose Network                     │    │
│  │                                                           │    │
│  │   ┌──────────────┐    ┌──────────────┐                   │    │
│  │   │   nginx       │    │   certbot     │                   │    │
│  │   │  :80 → :443   │    │  (SSL certs)  │                   │    │
│  │   │               │    └──────────────┘                   │    │
│  │   │  React SPA    │                                       │    │
│  │   │  (index.html) │                                       │    │
│  │   │               │                                       │    │
│  │   │  Reverse Proxy │                                      │    │
│  │   │  /api/* ──────┼──→ ┌──────────────┐                  │    │
│  │   │  /admin/* ────┼──→ │   web          │                  │    │
│  │   │  /accounts/* ─┼──→ │  (Gunicorn)   │                  │    │
│  │   │  /billings/* ─┼──→ │   :8000       │                  │    │
│  │   │  /businesses/*┼──→ │               │                  │    │
│  │   └──────────────┘    │  Django API   │                  │    │
│  │                        │  DRF + JWT    │                  │    │
│  │   Volumes:             │  Playwright   │                  │    │
│  │   /app/staticfiles ←──│  (PDF gen)    │                  │    │
│  │   /app/media ←────────│               │                  │    │
│  │                        │       │       │                  │    │
│  │                        └───────┼───────┘                  │    │
│  │                                │                           │    │
│  │                        ┌───────▼───────┐                  │    │
│  │                        │   db           │                  │    │
│  │                        │  PostgreSQL 15 │                  │    │
│  │                        │   :5432        │                  │    │
│  │                        └──────────────┘                  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### Docker Images

| Image | Base | Size | Built From |
|-------|------|------|------------|
| `invoices-web` | python:3.13-slim | ~1.5 GB | `Dockerfile.prod` (includes Playwright Chromium) |
| `invoices-nginx` | nginx:1.27-alpine | ~50 MB | `nginx/Dockerfile` (multi-stage: Node.js build → Nginx) |
| `postgres:15-alpine` | alpine | ~80 MB | Official image (pulled, not built) |

### Docker Volumes

| Volume | Mounted At | Purpose |
|--------|-----------|---------|
| `postgres_data` | `/var/lib/postgresql/data/` | Database persistence |
| `static_data` | `/app/staticfiles/` | Django admin/DRF CSS + JS |
| `media_data` | `/app/media/` | User-uploaded files (logos) |
| `certbot_conf` | `/etc/letsencrypt/` | SSL certificates |
| `certbot_www` | `/var/www/certbot/` | ACME challenge files |

### Request Flow

```
Browser → http://152.70.79.182
  → Nginx (:80)
    → /api/*, /admin/*, /accounts/*, /billings/*, /businesses/*
        → Proxy to Gunicorn (web:8000) → Django → PostgreSQL
    → /static/*
        → Serve from /app/staticfiles/ (Docker volume)
    → /media/*
        → Serve from /app/media/ (Docker volume)
    → Everything else
        → Serve React SPA (/usr/share/nginx/html/index.html)
        → React Router handles client-side routing
```

---

## Quick Reference — Most Used Commands

```bash
# SSH into the server
ssh -i "$SSH_KEY" ubuntu@152.70.79.182

# Go to app directory
cd /opt/invoices

# Start everything
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Stop everything
docker compose -f docker-compose.prod.yml --env-file .env.prod down

# View logs
docker compose -f docker-compose.prod.yml logs -f --tail=50

# Deploy an update
git pull origin main
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Django management commands
docker compose -f docker-compose.prod.yml exec web python manage.py <command>

# Database backup
docker compose -f docker-compose.prod.yml exec db pg_dump -U invoices invoices > backup.sql

# Check container status
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```

---

## Credentials (Current Deployment)

| User | Username | Password | Purpose |
|------|----------|----------|---------|
| Admin | `admin` | `AdminInvoices2026x` | Full access + Django admin |
| Guest | `guest` | `GuestDemo2026x` | Demo login button on frontend |
| Test | `testuser` | `password123` | Created by dummy data script |

> **Change these passwords** for a real production deployment.

---

## Files Involved in the Deployment

| File | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Production compose — 4 services, 5 volumes, 1 network |
| `Dockerfile.prod` | Django image — Python 3.13 + Gunicorn + Playwright Chromium |
| `nginx/Dockerfile` | Multi-stage — Node.js builds React → Nginx serves it |
| `nginx/default.conf` | Nginx HTTP config (used initially, before SSL) |
| `nginx/default-ssl.conf` | Nginx HTTPS config (swap in after certbot) |
| `.env.prod.example` | Template for environment variables |
| `.env.prod` | Actual env vars (on server only, NOT in git) |
| `server-setup.sh` | One-time VM setup script |
