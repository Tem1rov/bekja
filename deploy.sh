#!/bin/bash
# FMS Deployment Script for VPS
# Run as root on Ubuntu/Debian

set -e

echo "=== FMS Deployment Script ==="
echo ""

# Update system
echo "[1/6] Updating system..."
apt-get update -y
apt-get upgrade -y

# Install Docker
echo "[2/6] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
else
    echo "Docker already installed"
fi

# Install Docker Compose
echo "[3/6] Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose-plugin
fi

# Create project directory
echo "[4/6] Creating project directory..."
mkdir -p /opt/fms
cd /opt/fms

# Create docker-compose.yml
echo "[5/6] Creating configuration..."
cat > docker-compose.yml << 'DOCKER_COMPOSE'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: fms-postgres
    restart: always
    environment:
      POSTGRES_USER: fms
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-fms_secure_password_2024}
      POSTGRES_DB: fms
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fms"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fms_network

  redis:
    image: redis:7-alpine
    container_name: fms-redis
    restart: always
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - fms_network

  backend:
    image: python:3.11-slim
    container_name: fms-backend
    restart: always
    working_dir: /app
    environment:
      DATABASE_URL: postgresql+asyncpg://fms:${POSTGRES_PASSWORD:-fms_secure_password_2024}@postgres:5432/fms
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY:-your-super-secret-key-change-in-production-min-32-chars}
      ENVIRONMENT: production
      DEBUG: "false"
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    command: >
      bash -c "pip install -r requirements.txt && 
               alembic upgrade head && 
               uvicorn app.main:app --host 0.0.0.0 --port 8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - fms_network

  frontend:
    image: node:20-alpine
    container_name: fms-frontend
    restart: always
    working_dir: /app
    environment:
      VITE_API_URL: http://localhost:8000
    ports:
      - "3000:5173"
    volumes:
      - ./frontend:/app
    command: sh -c "npm install && npm run dev -- --host 0.0.0.0"
    networks:
      - fms_network

  nginx:
    image: nginx:alpine
    container_name: fms-nginx
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
      - frontend
    networks:
      - fms_network

volumes:
  postgres_data:
  redis_data:

networks:
  fms_network:
    driver: bridge
DOCKER_COMPOSE

# Create nginx config
mkdir -p nginx
cat > nginx/default.conf << 'NGINX_CONF'
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:5173;
}

server {
    listen 80;
    server_name _;

    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    location /docs {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location /openapi.json {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
NGINX_CONF

# Create .env file
cat > .env << 'ENV_FILE'
POSTGRES_PASSWORD=fms_secure_password_2024
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ENV_FILE

echo "[6/6] Deployment complete!"
echo ""
echo "=== Next Steps ==="
echo "1. Upload backend and frontend folders to /opt/fms/"
echo "2. Run: cd /opt/fms && docker compose up -d"
echo "3. Access the system at http://YOUR_SERVER_IP"
echo ""
echo "Server IP: $(curl -s ifconfig.me)"
