# Runbook: Server Ops

## Preflight

```bash
df -h
free -h
sudo ss -tulpn
sudo systemctl status apache2 --no-pager
sudo systemctl status docker --no-pager
sudo systemctl status srv1cv8-8.5.1.1150.service --no-pager
sudo systemctl status postgrespro-std-14.service --no-pager
sudo apachectl -S
```

## Apache change

```bash
sudo apachectl configtest
sudo systemctl reload apache2
```

## n8n check

```bash
cd /Storage/docker/n8n
sudo docker ps
sudo docker logs --tail=80 n8n
curl -I http://127.0.0.1:5678
curl -I https://n8n.3develop.ru
```

## Docker root check

```bash
sudo docker info | grep "Docker Root Dir"
```

Expected:

```text
Docker Root Dir: /Storage/docker-data
```

## Forbidden without review

```bash
sudo apt autoremove
sudo docker system prune -a
sudo docker volume prune
```
