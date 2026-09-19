# Despliegue en VPS

Esta guía prepara el proyecto para desplegarse en un servidor Ubuntu/Debian con Docker y Nginx.

## Requisitos

- VPS con Ubuntu 22.04 o 24.04
- dominio apuntando al servidor
- acceso SSH con usuario sudo
- puertos 22, 80 y 443 abiertos

## 1. Conectar al servidor

```bash
ssh usuario@tu-vps-ip
```

## 2. Clonar o preparar el proyecto

```bash
sudo mkdir -p /opt/centro_viajero
cd /opt/centro_viajero
sudo git clone https://github.com/juancho-pichaland/centro_viajero.git .
```

## 3. Configurar variables de producción

Copia y ajusta el ejemplo:

```bash
cp .env.production.example .env
nano .env
```

Completa los valores reales:

- `ALLOWED_ORIGINS=https://tu-dominio.com,https://www.tu-dominio.com`
- `POSTGRES_PASSWORD=<password_fuerte>`
- `DATABASE_URL=postgresql://postgres:<password>@db:5432/centro_viajero`
- `JWT_SECRET=<secret_largo>`
- `JWT_REFRESH_SECRET=<secret_largo_distinto>`
- `OLLAMA_MODEL=llama3.2:latest`

## 4. Instalar Docker y levantar la app

Ejecuta:

```bash
chmod +x scripts/deploy-vps.sh
sudo ./scripts/deploy-vps.sh
```

> El script instala Docker, abre puertos, solicita certificación TLS y levanta la app con `docker-compose.prod.yml`.

## 5. Verificar servicio

```bash
docker compose -f docker-compose.prod.yml --env-file .env ps
docker compose -f docker-compose.prod.yml --env-file .env logs -f
```

## 6. Validaciones rápidas

- Frontend: `https://tu-dominio.com`
- API: `https://tu-dominio.com/docs`
- Base de datos: accesible solo internamente por Docker
- Ollama: solo accesible dentro de la red interna

## 7. Recomendación de seguridad

- usa un usuario no root para administración
- revisa `ufw` y limita acceso innecesario
- usa GitHub Actions con approvals antes del despliegue
- mantén TLS y certificados renovados automáticamente

## 8. Rollback

```bash
docker compose -f docker-compose.prod.yml --env-file .env down
git pull origin main
sudo ./scripts/deploy-vps.sh
```

## 9. Actualizaciones futuras

```bash
git pull origin main
cp .env.production.example .env
# revisar cambios e iniciar la aplicación de nuevo
sudo ./scripts/deploy-vps.sh
```
