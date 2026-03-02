# Django Invoice App - Oracle Cloud Deployment Guide

## Prerequisites
- Oracle Cloud instance running Ubuntu
- SSH key pair generated
- Public IP: `152.70.79.182`

## Step 1: Configure Oracle Cloud Security Rules

**IMPORTANT:** Before you can SSH into your instance, you need to configure the firewall rules in Oracle Cloud Console.

### Open Required Ports:

1. Go to **Oracle Cloud Console** → **Compute** → **Instances**
2. Click on your instance name
3. Under **Resources**, click **Virtual Cloud Network → Default Security List**
4. Click **Add Ingress Rules** and add the following rules:

| Source CIDR | Protocol | Port Range | Description |
|-------------|----------|------------|-------------|
| 0.0.0.0/0   | TCP      | 22         | SSH Access  |
| 0.0.0.0/0   | TCP      | 80         | HTTP        |
| 0.0.0.0/0   | TCP      | 443        | HTTPS       |

**Note:** For better security, replace `0.0.0.0/0` with your specific IP address for SSH access.

## Step 2: Connect to Your Server

Once the firewall rules are configured, test the connection:

```bash
# Test connection (from your local machine)
ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182
```

If you see a warning about authenticity, type `yes` to continue.

## Step 3: Run the Server Setup Script

### Option A: Upload and run the script

```bash
# From your local machine, upload the script
scp -i ssh-key-2026-03-02.key server-setup.sh ubuntu@152.70.79.182:~/

# Connect to the server
ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182

# Make the script executable and run it
chmod +x server-setup.sh
./server-setup.sh
```

### Option B: Run commands directly

Connect to your server and paste the commands:

```bash
# 1. Update the system
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. Setup Permissions (So GitHub Actions doesn't need 'sudo')
sudo usermod -aG docker $USER
newgrp docker

# 4. Install Docker Compose
sudo apt-get install docker-compose-plugin -y

# 5. Install additional tools
sudo apt-get install -y git nginx certbot python3-certbot-nginx fail2ban

# 6. Configure Ubuntu's internal firewall
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# Save firewall rules
sudo apt-get install -y iptables-persistent netfilter-persistent
sudo netfilter-persistent save

# 7. Enable fail2ban for security
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Step 4: Verify Installation

After the script completes, log out and log back in:

```bash
exit
ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182
```

Verify Docker is working:

```bash
docker --version
docker compose version
```

## Step 5: Deploy Your Application

### 1. Clone your repository

```bash
git clone https://github.com/YOUR_USERNAME/Invoices.git
cd Invoices
```

### 2. Create environment file

```bash
nano .env
```

Add your production environment variables:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=152.70.79.182,yourdomain.com
DB_NAME=invoices
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=db
DB_PORT=5432
GUEST_USERNAME=testuser
GUEST_PASSWORD=password123
```

### 3. Start the application

```bash
docker compose up -d
```

### 4. Run migrations and create superuser

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic --noinput
```

## Step 6: Configure Nginx as Reverse Proxy

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/invoices
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name 152.70.79.182;  # Replace with your domain later

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/ubuntu/Invoices/staticfiles/;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/invoices /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 7: Configure SSL (Optional but Recommended)

After setting up a domain name:

```bash
sudo certbot --nginx -d yourdomain.com
```

## Troubleshooting

### SSH Connection Refused
- Check Oracle Cloud Security List rules
- Verify instance is running
- Check SSH service: `sudo systemctl status ssh`

### Cannot Access Web Application
- Check Docker containers: `docker compose ps`
- Check logs: `docker compose logs web`
- Verify Nginx: `sudo systemctl status nginx`
- Check firewall rules: `sudo iptables -L`

### Permission Denied for Docker
- You need to log out and back in after adding user to docker group
- Or run: `newgrp docker`

## Next Steps

1. Set up automatic deployments with GitHub Actions
2. Configure domain name
3. Set up SSL certificate with Let's Encrypt
4. Configure database backups
5. Set up monitoring and logging

## Useful Commands

```bash
# View running containers
docker compose ps

# View logs
docker compose logs -f web

# Restart application
docker compose restart

# Stop application
docker compose down

# Update application
git pull
docker compose up -d --build
```
