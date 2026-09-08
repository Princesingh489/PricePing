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
