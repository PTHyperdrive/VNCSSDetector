# VNCSSDetector Web Service

A centralized web service for managing VNCSSDetector nodes on Ubuntu 24.04 with MySQL.

## Requirements

- Ubuntu 24.04 LTS
- Python 3.12+
- MySQL 8.0+
- Redis 7.0+
- Node.js 20+ (for frontend)

## Quick Start

### 1. Install Dependencies

```bash
# System dependencies
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip mysql-server redis-server nginx

# Create Python virtual environment
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Database

```bash
# Login to MySQL
sudo mysql

# Create database and user
CREATE DATABASE vncssd_web CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'vncssd'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON vncssd_web.* TO 'vncssd'@'localhost';
FLUSH PRIVILEGES;
EXIT;

# Run migrations
alembic upgrade head
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Development Server

```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (in another terminal)
cd frontend
npm install
npm run dev
```

## Production Deployment

See [deploy/README.md](deploy/README.md) for production deployment instructions.

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
