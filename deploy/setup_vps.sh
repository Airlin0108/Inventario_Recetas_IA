#!/bin/bash
# Script de configuracion inicial para VPS Ubuntu 22.04
# Uso: bash setup_vps.sh

set -e

echo "==> Actualizando paquetes del sistema..."
apt-get update && apt-get upgrade -y

echo "==> Instalando Docker y Docker Compose..."
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "==> Instalando Nginx y Certbot..."
apt-get install -y nginx certbot python3-certbot-nginx

echo "==> Clonando el repositorio..."
git clone https://github.com/Airlin0108/Inventario_Recetas_IA.git /app
cd /app

echo "==> Creando archivo .env (completar manualmente)..."
cp .env.example .env
echo "IMPORTANTE: edita /app/.env con tus credenciales antes de continuar"

echo "==> Copiando configuracion de Nginx..."
cp deploy/nginx.conf /etc/nginx/sites-available/inventario-recetas
ln -sf /etc/nginx/sites-available/inventario-recetas /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo "==> Obteniendo certificado SSL con Certbot..."
echo "Ejecuta manualmente: certbot --nginx -d tu-dominio.com"

echo "==> Levantando contenedores Docker..."
echo "Ejecuta: cd /app && docker compose up -d --build"

echo "==> Configuracion base completada."
