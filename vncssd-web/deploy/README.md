# Deployment Guide

This directory contains deployment configurations for VNCSSDetector Web Service on Ubuntu 24.04.

## Files

- `install.sh` - Automated installation script
- `vncssd-web.service` - systemd service file
- `nginx.conf` - Nginx reverse proxy configuration

## Quick Deployment

### 1. Clone the repository

```bash
git clone <repository-url> /tmp/vncssd-web
cd /tmp/vncssd-web
```

### 2. Run the installation script

```bash
sudo bash deploy/install.sh
```

### 3. Configure your domain

Edit `/etc/nginx/sites-available/vncssd-web` and replace `vncssd.example.com` with your actual domain.

### 4. Obtain SSL certificate

```bash
sudo certbot --nginx -d your-domain.com
```

### 5. Verify installation

```bash
sudo systemctl status vncssd-web
curl -k https://localhost/api/health
```

## Manual Deployment

If you prefer manual installation, follow these steps:

### Prerequisites

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv mysql-server redis-server nginx
```

### Database Setup

```bash
sudo mysql
```

```sql
CREATE DATABASE vncssd_web CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'vncssd'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON vncssd_web.* TO 'vncssd'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Import schema:
```bash
sudo mysql vncssd_web < database/schema.sql
```

### Backend Setup

```bash
# Create installation directory
sudo mkdir -p /opt/vncssd-web
sudo cp -r backend /opt/vncssd-web/

# Create virtual environment
cd /opt/vncssd-web/backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings
```

### Service Setup

```bash
sudo cp deploy/vncssd-web.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable vncssd-web
sudo systemctl start vncssd-web
```

### Nginx Setup

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/vncssd-web
sudo ln -s /etc/nginx/sites-available/vncssd-web /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Maintenance

### View logs

```bash
# Service logs
sudo journalctl -u vncssd-web -f

# Nginx access logs
sudo tail -f /var/log/nginx/vncssd-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/vncssd-error.log
```

### Restart service

```bash
sudo systemctl restart vncssd-web
```

### Update application

```bash
cd /opt/vncssd-web
sudo -u vncssd git pull
sudo -u vncssd bash -c 'source backend/venv/bin/activate && pip install -r backend/requirements.txt'
sudo systemctl restart vncssd-web
```

### Database backup

```bash
mysqldump -u vncssd -p vncssd_web > backup_$(date +%Y%m%d).sql
```

### Database restore

```bash
mysql -u vncssd -p vncssd_web < backup_20240101.sql
```

## Troubleshooting

### Service won't start

Check the logs:
```bash
sudo journalctl -u vncssd-web -n 50
```

Common issues:
- Database connection failed: Check MySQL is running and credentials are correct
- Port already in use: Check if another service is using port 8000
- Permission denied: Check file ownership and permissions

### WebSocket connections failing

Ensure Nginx is configured for WebSocket upgrades:
```nginx
location /ws/ {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### High memory usage

Adjust the number of workers in the service file:
```ini
ExecStart=... --workers 2
```

## Security Checklist

- [ ] Changed default admin password
- [ ] SSL certificate installed
- [ ] Firewall configured (only ports 80, 443 open)
- [ ] Regular backups scheduled
- [ ] Log rotation configured
- [ ] Fail2ban installed for brute-force protection
