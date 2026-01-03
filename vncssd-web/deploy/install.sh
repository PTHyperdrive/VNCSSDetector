#!/bin/bash
# VNCSSDetector Web Service - Installation Script for Ubuntu 24.04
# Run as root: sudo bash install.sh

set -e

echo "=========================================="
echo "VNCSSDetector Web Service Installation"
echo "Ubuntu 24.04 LTS"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/opt/vncssd-web"
DATA_DIR="/var/lib/vncssd"
SERVICE_USER="vncssd"
MYSQL_DB="vncssd_web"
MYSQL_USER="vncssd"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root${NC}"
   exit 1
fi

# Prompt for MySQL password
read -sp "Enter MySQL password for vncssd user: " MYSQL_PASSWORD
echo
read -sp "Confirm MySQL password: " MYSQL_PASSWORD_CONFIRM
echo

if [[ "$MYSQL_PASSWORD" != "$MYSQL_PASSWORD_CONFIRM" ]]; then
    echo -e "${RED}Passwords do not match${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Installing system dependencies...${NC}"
apt update
apt install -y \
    python3.12 \
    python3.12-venv \
    python3-pip \
    mysql-server \
    redis-server \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl

echo -e "${YELLOW}Step 2: Creating service user...${NC}"
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -m -d "$INSTALL_DIR" "$SERVICE_USER"
    echo -e "${GREEN}Created user: $SERVICE_USER${NC}"
else
    echo -e "${GREEN}User $SERVICE_USER already exists${NC}"
fi

echo -e "${YELLOW}Step 3: Creating directories...${NC}"
mkdir -p "$INSTALL_DIR"
mkdir -p "$DATA_DIR/recordings"
mkdir -p /var/log/vncssd

echo -e "${YELLOW}Step 4: Configuring MySQL...${NC}"
# Start MySQL if not running
systemctl start mysql
systemctl enable mysql

# Create database and user
mysql -e "CREATE DATABASE IF NOT EXISTS $MYSQL_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS '$MYSQL_USER'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';"
mysql -e "GRANT ALL PRIVILEGES ON $MYSQL_DB.* TO '$MYSQL_USER'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Import schema
if [[ -f "database/schema.sql" ]]; then
    mysql $MYSQL_DB < database/schema.sql
    echo -e "${GREEN}Database schema imported${NC}"
fi

echo -e "${YELLOW}Step 5: Configuring Redis...${NC}"
systemctl start redis-server
systemctl enable redis-server

echo -e "${YELLOW}Step 6: Setting up Python environment...${NC}"
cp -r backend "$INSTALL_DIR/"
cd "$INSTALL_DIR/backend"

python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${YELLOW}Step 7: Creating environment file...${NC}"
# Generate a random secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

cat > "$INSTALL_DIR/backend/.env" << EOF
# VNCSSDetector Web Service Configuration
# Generated on $(date)

# Database
DATABASE_URL=mysql+aiomysql://${MYSQL_USER}:${MYSQL_PASSWORD}@localhost:3306/${MYSQL_DB}

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Settings
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server Settings
DEBUG=false
ALLOWED_ORIGINS=https://vncssd.example.com

# File Storage
RECORDINGS_PATH=${DATA_DIR}/recordings
MAX_UPLOAD_SIZE_MB=500

# Logging
LOG_LEVEL=INFO
EOF

chmod 600 "$INSTALL_DIR/backend/.env"

echo -e "${YELLOW}Step 8: Setting up frontend...${NC}"
if [[ -d "frontend" ]]; then
    cp -r frontend "$INSTALL_DIR/"
    cd "$INSTALL_DIR/frontend"
    
    # Install Node.js if not present
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt install -y nodejs
    fi
    
    npm install
    npm run build
    echo -e "${GREEN}Frontend built successfully${NC}"
fi

echo -e "${YELLOW}Step 9: Setting permissions...${NC}"
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR"
chown -R "$SERVICE_USER:$SERVICE_USER" /var/log/vncssd

echo -e "${YELLOW}Step 10: Installing systemd service...${NC}"
cp deploy/vncssd-web.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable vncssd-web
systemctl start vncssd-web

echo -e "${YELLOW}Step 11: Configuring Nginx...${NC}"
cp deploy/nginx.conf /etc/nginx/sites-available/vncssd-web
ln -sf /etc/nginx/sites-available/vncssd-web /etc/nginx/sites-enabled/

# Test nginx configuration
nginx -t

systemctl restart nginx

echo ""
echo -e "${GREEN}=========================================="
echo "Installation Complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Update /etc/nginx/sites-available/vncssd-web with your domain"
echo "2. Obtain SSL certificate: sudo certbot --nginx -d vncssd.example.com"
echo "3. Check service status: sudo systemctl status vncssd-web"
echo "4. View logs: sudo journalctl -u vncssd-web -f"
echo ""
echo "Default admin credentials:"
echo "  Email: admin@vncssd.local"
echo "  Password: admin123"
echo ""
echo -e "${YELLOW}IMPORTANT: Change the admin password immediately!${NC}"
