set -e
cd /Storage/docker/n8n
PW='159753'
echo "$PW" | sudo -S cp docker-compose.yml docker-compose.yml.bak.$(date +%Y%m%d_%H%M%S)
echo "$PW" | sudo -S cp /etc/apache2/sites-available/n8n.3develop.ru-le-ssl.conf /etc/apache2/sites-available/n8n.3develop.ru-le-ssl.conf.bak.$(date +%Y%m%d_%H%M%S)
cat > /tmp/docker-compose.n8n.new <<'EOF'
version: "2.4"

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "127.0.0.1:5678:5678"
    environment:
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=https://n8n.3develop.ru/
      - GENERIC_TIMEZONE=Europe/Moscow
      - TZ=Europe/Moscow
      - N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS=true
    volumes:
      - ./n8n_data:/home/node/.n8n
    mem_limit: 512m
EOF
cat > /tmp/n8n.ssl.new <<'EOF'
<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName n8n.3develop.ru

    ErrorLog ${APACHE_LOG_DIR}/n8n_error.log
    CustomLog ${APACHE_LOG_DIR}/n8n_access.log combined

    SSLCertificateFile /etc/letsencrypt/live/n8n.3develop.ru/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/n8n.3develop.ru/privkey.pem
    Include /etc/letsencrypt/options-ssl-apache.conf

    ProxyPreserveHost On
    ProxyRequests Off

    ProxyPass "/rest/push" "ws://127.0.0.1:5678/rest/push"
    ProxyPassReverse "/rest/push" "ws://127.0.0.1:5678/rest/push"

    ProxyPass / http://127.0.0.1:5678/
    ProxyPassReverse / http://127.0.0.1:5678/

    RequestHeader set X-Forwarded-Proto "https" early
</VirtualHost>
</IfModule>
EOF
echo "$PW" | sudo -S mv /tmp/docker-compose.n8n.new /Storage/docker/n8n/docker-compose.yml
echo "$PW" | sudo -S mv /tmp/n8n.ssl.new /etc/apache2/sites-available/n8n.3develop.ru-le-ssl.conf
cd /Storage/docker/n8n
echo "$PW" | sudo -S docker-compose config >/tmp/n8n.compose.check
echo "$PW" | sudo -S docker-compose up -d
echo "$PW" | sudo -S apachectl configtest
echo "$PW" | sudo -S systemctl reload apache2
printf '%s\n' '--- LOCAL HEALTHZ ---'
curl -sS -D - http://127.0.0.1:5678/healthz -o /dev/null
printf '%s\n' '--- PUBLIC HEALTHZ ---'
curl -sS -D - https://n8n.3develop.ru/healthz -o /dev/null
printf '%s\n' '--- CURRENT SSL CONF ---'
sed -n '1,220p' /etc/apache2/sites-available/n8n.3develop.ru-le-ssl.conf
printf '%s\n' '--- DOCKER LOGS ---'
docker logs --tail 60 n8n 2>&1
