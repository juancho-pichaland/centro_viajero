#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="${REPO_DIR:-/opt/centro_viajero}"
BRANCH="${BRANCH:-main}"
DOMAIN="${DOMAIN:-tu-dominio.com}"
EMAIL="${EMAIL:-admin@tu-dominio.com}"

echo "[1/5] Installing base dependencies..."
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl git ufw docker.io docker-compose-plugin certbot python3-certbot-nginx

systemctl enable docker
systemctl start docker

echo "[2/5] Preparing project directory..."
mkdir -p "$REPO_DIR"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone https://github.com/juancho-pichaland/centro_viajero.git "$REPO_DIR"
fi
cd "$REPO_DIR"
git fetch origin
git checkout "$BRANCH"
git pull origin "$BRANCH"

if [ ! -f .env ]; then
  cp .env.production.example .env
  echo "Created .env from example. Please edit it before continuing."
  echo "Set DOMAIN, JWT secrets, PostgreSQL password and allowed origins."
  exit 1
fi

if [ ! -d certs ]; then
  mkdir -p certs
fi

if [ ! -f certs/fullchain.pem ] || [ ! -f certs/privkey.pem ]; then
  echo "[3/5] Requesting TLS certificate with Let's Encrypt..."
  certbot certonly --standalone --agree-tos --email "$EMAIL" -d "$DOMAIN" -d "www.$DOMAIN" || true
  install -m 0644 "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" certs/fullchain.pem
  install -m 0600 "/etc/letsencrypt/live/$DOMAIN/privkey.pem" certs/privkey.pem
fi

echo "[4/5] Opening firewall ports..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "[5/5] Starting production deployment..."
docker compose -f docker-compose.prod.yml --env-file .env up -d --build

echo "Deployment started successfully."
echo "Check status with: docker compose -f docker-compose.prod.yml --env-file .env ps"
echo "Logs: docker compose -f docker-compose.prod.yml --env-file .env logs -f"
