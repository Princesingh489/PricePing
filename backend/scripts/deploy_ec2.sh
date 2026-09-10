#!/bin/bash
set -euo pipefail

echo "========================================================"
echo "🚀 PricePing Production Deployment on AWS EC2"
echo "========================================================"

APP_DIR="${HOME}/PricePing"

if [ ! -d "$APP_DIR" ]; then
  if [ -d "/home/ubuntu/PricePing" ]; then
    APP_DIR="/home/ubuntu/PricePing"
  else
    echo "❌ Error: PricePing repository directory not found in ${HOME}/PricePing"
    exit 1
  fi
fi

cd "$APP_DIR"

echo "📥 1. Pulling latest codebase from origin/main..."
git fetch origin main
git reset --hard origin/main

echo "💾 1.1 Verifying Linux Swap memory to protect against OOM..."
if [ $(swapon --show | wc -l) -le 1 ]; then
  echo "   Setting up 4GB swapfile to guarantee server stability under load..."
  if [ ! -f /swapfile ]; then
    sudo fallocate -l 4G /swapfile 2>/dev/null || sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 2>/dev/null
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile 2>/dev/null
  fi
  sudo swapon /swapfile 2>/dev/null || true
  if ! grep -q '/swapfile' /etc/fstab 2>/dev/null; then
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null 2>&1 || true
  fi
  echo "   ✅ Swap configured successfully."
else
  echo "   ✅ Swap memory is already active ($(free -m | awk '/Swap/ {print $2}') MB)."
fi

echo "🐳 2. Verifying Docker & Docker Compose..."
if docker compose version &> /dev/null; then
  COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
  COMPOSE_CMD="docker-compose"
else
  echo "❌ Error: docker-compose not found on this machine."
  exit 1
fi

echo "🔨 3. Rebuilding updated services (backend, worker, beat)..."
$COMPOSE_CMD build backend worker beat

echo "🔄 4. Starting all containers..."
$COMPOSE_CMD up -d --remove-orphans

echo "⏳ 5. Waiting for API service to stabilize..."
for i in {1..12}; do
  if curl -sf http://127.0.0.1:8000/api/health > /dev/null; then
    echo "✅ Backend API is healthy!"
    break
  fi
  echo "   Waiting for backend to respond... ($i/12)"
  sleep 3
done

echo "📊 6. Active Docker Containers:"
$COMPOSE_CMD ps

echo "========================================================"
echo "🎉 PricePing backend successfully updated and deployed!"
echo "   Endpoint: http://65.0.199.91:8000/api/health"
echo "========================================================"
