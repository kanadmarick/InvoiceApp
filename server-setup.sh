#!/bin/bash
set -e

# =============================================================
# Oracle Cloud VM — Initial Server Setup Script
# For Ubuntu 22.04+ on OCI Always Free Tier (ARM Ampere A1)
#
# Run this ONCE on a fresh VM:
#   ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182
#   curl -sSL https://raw.githubusercontent.com/YOUR_REPO/main/server-setup.sh | bash
#   OR: copy this file to the server and run: bash server-setup.sh
# =============================================================

echo "============================================"
echo "Django Invoice App - OCI Server Setup"
echo "============================================"
echo ""

# 1. Update the system
echo "Step 1: Updating system packages..."
sudo apt-get update && sudo apt-get upgrade -y

# 2. Install Docker
echo ""
echo "Step 2: Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# 3. Setup Docker permissions
echo ""
echo "Step 3: Configuring Docker permissions..."
sudo usermod -aG docker $USER

# 4. Install Docker Compose
echo ""
echo "Step 4: Installing Docker Compose plugin..."
sudo apt-get install -y docker-compose-plugin

# 5. Install additional tools
echo ""
echo "Step 5: Installing security tools..."
sudo apt-get install -y git fail2ban

# 6. Configure OCI iptables firewall
# OCI Ubuntu images use iptables (not ufw). Must open ports 80/443.
echo ""
echo "Step 6: Configuring OCI firewall (iptables)..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# Persist iptables rules across reboots
sudo apt-get install -y iptables-persistent netfilter-persistent
sudo netfilter-persistent save

# 7. Start and enable fail2ban
echo ""
echo "Step 7: Configuring fail2ban for SSH protection..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 8. Create app directory
echo ""
echo "Step 8: Creating application directory..."
sudo mkdir -p /opt/invoices
sudo chown $USER:$USER /opt/invoices

# 9. Set up automatic security updates
echo ""
echo "Step 9: Enabling automatic security updates..."
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades 2>/dev/null || true

# 10. Create SSL cert renewal cron job
echo ""
echo "Step 10: Creating SSL renewal cron job..."
(crontab -l 2>/dev/null; echo "0 3 * * * cd /opt/invoices && docker compose -f docker-compose.prod.yml run --rm certbot renew && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload") | crontab -

echo ""
echo "============================================"
echo "Server setup complete!"
echo "============================================"
echo ""
echo "IMPORTANT: Log out and log back in for Docker permissions to take effect."
echo "Run: exit"
echo "Then reconnect: ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182"
echo ""
echo "Next steps (see DEPLOYMENT_GUIDE.md for details):"
echo "  1. Clone the repository to /opt/invoices"
echo "  2. Copy .env.prod.example to .env.prod and fill in values"
echo "  3. Run: docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build"
echo "  4. Obtain SSL certificate with certbot"
echo "  5. Switch to SSL nginx config"
echo ""
