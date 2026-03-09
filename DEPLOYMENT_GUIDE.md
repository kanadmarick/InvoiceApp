# Django Invoice App — Oracle Cloud Deployment Guide

Complete guide to deploy on **Oracle Cloud Always Free Tier** (ARM Ampere A1, 4 OCPUs, 24 GB RAM).

---

## Architecture

```
Internet → Nginx (:80/:443) ─┬─ React SPA (static files)
                              ├─ /admin/        → Gunicorn (:8000)
                              ├─ /accounts/     → Gunicorn (:8000)
                              ├─ /businesses/   → Gunicorn (:8000)
                              ├─ /billings/     → Gunicorn (:8000)
                              ├─ /api/          → Gunicorn (:8000)
                              ├─ /static/       → Docker volume
                              └─ /media/        → Docker volume
                                    │
                              PostgreSQL (:5432) — internal only
```

**Docker services:** `nginx` (Nginx + React build), `web` (Django + Gunicorn), `db` (PostgreSQL 15), `certbot` (SSL)

---

## Prerequisites

| Item | Details |
|------|---------|
| OCI Account | Free Tier with Always Free resources |
| SSH Key | `ssh-key-2026-03-02.key` (your private key) |
| VM Public IP | `152.70.79.182` |
| Domain (optional) | Point an A record to `152.70.79.182` |
| Git repo | Your Invoices repository pushed to GitHub |

---

## Step 1: OCI Console — Security List

Before connecting, open ports in **OCI Console → Networking → VCN → Default Security List → Add Ingress Rules**:

| Source CIDR | Protocol | Port | Description |
|-------------|----------|------|-------------|
| 0.0.0.0/0 | TCP | 22 | SSH |
| 0.0.0.0/0 | TCP | 80 | HTTP |
| 0.0.0.0/0 | TCP | 443 | HTTPS |

> **Tip:** Restrict SSH (port 22) to your IP for better security.

---

## Step 2: Connect via SSH

```bash
ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182
```

---

## Step 3: Run Server Setup Script

Upload and execute the setup script (installs Docker, Docker Compose, fail2ban, opens iptables ports):

```bash
# From your LOCAL machine — upload the script
scp -i ssh-key-2026-03-02.key server-setup.sh ubuntu@152.70.79.182:~/

# On the SERVER
chmod +x ~/server-setup.sh
~/server-setup.sh
```

**Important:** Log out and back in after running for Docker group permissions:

```bash
exit
ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182
```

Verify Docker works:

```bash
docker --version
docker compose version
```

---

## Step 4: Clone Repository

```bash
cd /opt/invoices
git clone https://github.com/YOUR_USERNAME/Invoices.git .
```

> If you ran `server-setup.sh`, the `/opt/invoices` directory already exists with correct ownership.

---

## Step 5: Configure Environment

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Fill in **all** values — at minimum:

```env
SECRET_KEY=<generate-a-real-key>
DEBUG=False
ALLOWED_HOSTS=YOUR_DOMAIN,152.70.79.182

POSTGRES_DB=invoices
POSTGRES_USER=invoices
POSTGRES_PASSWORD=<strong-random-password>

DB_ENGINE=django.db.backends.postgresql
DB_NAME=invoices
DB_USER=invoices
DB_PASSWORD=<same-password-as-above>
DB_HOST=db
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://152.70.79.182
CSRF_TRUSTED_ORIGINS=http://152.70.79.182

# Set to False until SSL is configured, then change to True
SECURE_SSL_REDIRECT=False

GUEST_USERNAME=guest
GUEST_PASSWORD=<guest-password>
```

Generate a secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## Step 6: Build and Start

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

This will:
1. **Build the Django image** (`Dockerfile.prod`) — installs Python deps, Playwright Chromium, collects static files
2. **Build the Nginx image** (`nginx/Dockerfile`) — builds React frontend with Vite, copies into Nginx
3. **Start PostgreSQL** and wait for health check
4. **Run Django migrations** automatically (the CMD in Dockerfile.prod runs `migrate` on startup)
5. **Start Gunicorn** with 3 workers

Check status:

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f
```

---

## Step 7: Create Superuser & Load Data

```bash
# Create admin account
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# (Optional) Load demo data
docker compose -f docker-compose.prod.yml exec web python manage.py populate_dummy_data
```

---

## Step 8: Test (HTTP)

Open in your browser:

- **React SPA:** `http://152.70.79.182`
- **Django Admin:** `http://152.70.79.182/admin/`
- **API Docs (Swagger):** `http://152.70.79.182/api/docs/`

If everything works, proceed to SSL setup.

---

## Step 9: SSL Certificate (Let's Encrypt)

> **Prerequisite:** You need a domain name pointing to `152.70.79.182`. If you only have an IP, skip this step and use HTTP.

### 9a. Obtain the certificate

```bash
docker compose -f docker-compose.prod.yml run --rm certbot \
  certonly --webroot -w /var/www/certbot -d YOUR_DOMAIN
```

### 9b. Switch Nginx to SSL config

```bash
# Edit the SSL template with your domain
sed 's/YOUR_DOMAIN/yourdomain.com/g' nginx/default-ssl.conf > nginx/default.conf

# Rebuild Nginx with the new config
docker compose -f docker-compose.prod.yml up -d --build nginx
```

### 9c. Update environment for HTTPS

Edit `.env.prod`:

```env
CORS_ALLOWED_ORIGINS=https://YOUR_DOMAIN
CSRF_TRUSTED_ORIGINS=https://YOUR_DOMAIN
SECURE_SSL_REDIRECT=True
```

Restart the web service:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d web
```

### 9d. Verify HTTPS

- `https://YOUR_DOMAIN` should show the React app
- `https://YOUR_DOMAIN/admin/` should show Django admin

### 9e. Auto-renewal

The `server-setup.sh` script already created a cron job for auto-renewal. Verify:

```bash
crontab -l
# Should show: 0 3 * * * ... certbot renew ...
```

---

## Updating the Application

```bash
cd /opt/invoices

# Pull latest code
git pull origin main

# Rebuild and restart (zero-downtime with --no-deps)
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Check logs
docker compose -f docker-compose.prod.yml logs -f --tail=50
```

---

## Useful Commands

```bash
# ── Status ────────────────────────────────────────────────────
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f web
docker compose -f docker-compose.prod.yml logs -f nginx
docker compose -f docker-compose.prod.yml logs -f db

# ── Django Management ─────────────────────────────────────────
docker compose -f docker-compose.prod.yml exec web python manage.py shell
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# ── Database ──────────────────────────────────────────────────
# Backup
docker compose -f docker-compose.prod.yml exec db pg_dump -U invoices invoices > backup_$(date +%Y%m%d).sql

# Restore
cat backup.sql | docker compose -f docker-compose.prod.yml exec -T db psql -U invoices invoices

# ── Restart / Stop ────────────────────────────────────────────
docker compose -f docker-compose.prod.yml restart web
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# ── Cleanup ───────────────────────────────────────────────────
docker system prune -af    # Remove unused images/containers (free disk space)
```

---

## Troubleshooting

### Can't connect via SSH
- Check OCI Security List has port 22 open
- Verify instance is **Running** in OCI Console
- Check your SSH key file permissions: `chmod 400 ssh-key-2026-03-02.key`

### Site not loading (connection refused)
- Check containers are running: `docker compose -f docker-compose.prod.yml ps`
- Check **OCI Security List** has ports 80/443 open
- Check **iptables**: `sudo iptables -L -n | grep -E '80|443'`
- Check Nginx logs: `docker compose -f docker-compose.prod.yml logs nginx`

### 502 Bad Gateway
- Gunicorn crashed — check: `docker compose -f docker-compose.prod.yml logs web`
- Database not ready — the web container waits for db health check, but check: `docker compose -f docker-compose.prod.yml logs db`

### Static files / CSS missing
- Verify static volume is shared: `docker compose -f docker-compose.prod.yml exec nginx ls /app/staticfiles/`
- Re-collect: `docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput`

### Admin panel CSS broken
- Static files are served by Nginx from the shared Docker volume
- Check `/static/` is routing correctly: `curl -I http://localhost/static/admin/css/base.css`

### Database connection refused
- Check db container is healthy: `docker compose -f docker-compose.prod.yml ps db`
- Verify DATABASE_URL in `docker compose -f docker-compose.prod.yml exec web env | grep DATABASE`

### Playwright / PDF generation fails
- Chromium needs ~500MB RAM — should be fine with 24GB on Free Tier
- Check: `docker compose -f docker-compose.prod.yml exec web playwright install --with-deps chromium`

---

## File Reference

| File | Purpose |
|------|---------|
| `docker-compose.prod.yml` | Production Docker Compose (web + db + nginx + certbot) |
| `Dockerfile.prod` | Django production image (Gunicorn + Playwright) |
| `nginx/Dockerfile` | Multi-stage: React build → Nginx image |
| `nginx/default.conf` | Nginx config (HTTP initially) |
| `nginx/default-ssl.conf` | Nginx config template (HTTPS — copy after getting cert) |
| `.env.prod.example` | Template for production environment variables |
| `server-setup.sh` | One-time OCI VM setup (Docker, firewall, fail2ban) |
