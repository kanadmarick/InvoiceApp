#!/bin/bash
set -e

echo "============================================"
echo "Django Invoice App - Server Setup Script"
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
echo "Step 4: Installing Docker Compose..."
sudo apt-get install docker-compose-plugin -y

# 5. Install additional tools
echo ""
echo "Step 5: Installing additional tools..."
sudo apt-get install -y git nginx certbot python3-certbot-nginx fail2ban

# 6. Configure firewall rules
echo ""
echo "Step 6: Configuring firewall (iptables)..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT

# Install netfilter-persistent to save rules
sudo apt-get install -y iptables-persistent netfilter-persistent
sudo netfilter-persistent save

# 7. Start and enable fail2ban
echo ""
echo "Step 7: Configuring fail2ban for security..."
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

echo ""
echo "============================================"
echo "✓ Server setup complete!"
echo "============================================"
echo ""
echo "IMPORTANT: You need to log out and log back in for Docker permissions to take effect."
echo "Run: exit"
echo "Then reconnect with: ssh -i ssh-key-2026-03-02.key ubuntu@152.70.79.182"
echo ""
echo "Next steps:"
echo "  1. Clone your repository"
echo "  2. Configure environment variables"
echo "  3. Set up Nginx reverse proxy"
echo "  4. Configure SSL with Let's Encrypt"
echo ""
