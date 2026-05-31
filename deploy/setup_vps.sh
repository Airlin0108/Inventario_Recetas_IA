#!/bin/bash
# =====================================================================
# Configuracion inicial de un VPS Ubuntu 22.04 para desplegar la app.
# SSL automatico mediante Caddy (no requiere Certbot ni Nginx).
#
# Uso (como root):  bash setup_vps.sh
# =====================================================================

set -e

echo "==> Actualizando paquetes del sistema..."
apt-get update && apt-get upgrade -y

echo "==> Instalando Docker y Docker Compose..."
apt-get install -y ca-certificates curl gnupg git
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

echo "==> Configurando firewall (UFW)..."
apt-get install -y ufw
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> Clonando el repositorio..."
git clone https://github.com/Airlin0108/Inventario_Recetas_IA.git /opt/inventario-recetas
cd /opt/inventario-recetas

echo "==> Creando archivo .env a partir de la plantilla..."
cp .env.example .env

cat <<'MSG'

============================================================
 SIGUIENTE PASO MANUAL — edita el archivo .env:

   nano /opt/inventario-recetas/.env

 Define obligatoriamente:
   - DOMAIN              (tu dominio, ej: recetas.midominio.com)
   - DATABASE_PASSWORD   (genera: openssl rand -base64 24)
   - SECRET_KEY          (genera: openssl rand -hex 32)
   - OPENROUTER_API_KEY  (tu clave de https://openrouter.ai/keys)

 Asegurate de que tu dominio (registro DNS tipo A) apunte
 a la IP publica de este servidor ANTES de levantar Caddy.

 Luego levanta todo en produccion con:

   cd /opt/inventario-recetas
   docker compose -f docker-compose.prod.yml up -d --build

 Caddy obtendra el certificado SSL automaticamente.
============================================================

MSG
