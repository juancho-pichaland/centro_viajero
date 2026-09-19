# Centro Viajero

Centro digital de orientación y preparación del viajero es una plataforma web pensada para ayudar a una persona antes, durante y después de un viaje. El proyecto combina una experiencia de usuario moderna con un backend API REST, autenticación, checklist de viaje, centro de información, solicitudes de soporte y un asistente inteligente orientado al viaje.

## Descripción general

La aplicación está pensada para que el usuario pueda:

- Revisar su viaje activo y estado de preparación
- Completar una checklist personalizada
- Consultar artículos, destinos y preguntas frecuentes
- Enviar solicitudes de ayuda o soporte
- Hablar con un asistente turístico basado en Ollama para recomendaciones y orientación práctica

La solución está dividida en dos partes principales:

- Frontend: React + Vite
- Backend: FastAPI + SQLAlchemy + PostgreSQL

## Stack tecnológico

- Frontend: React 18, Vite, React Router
- Backend: FastAPI, SQLAlchemy, Pydantic, JWT
- Base de datos: PostgreSQL 15
- Contenedores: Docker + Docker Compose
- IA local: Ollama
- Pruebas: pytest

## Funcionalidades principales

### Dashboard y gestión del viaje
- Resumen del viaje activo
- Estado de preparación
- Progreso visual de tareas pendientes
- Navegación a módulos del producto

### Checklist personal
- Tareas por categoría
- Marcar tareas como completadas
- Seguimiento del progreso

### Centro de información
- Artículos por categoría
- Filtros por destino y temática
- Preguntas frecuentes

### Solicitudes
- Crear incidencias o consultas
- Consultar historial de solicitudes
- Estado de atención

### Chatbot turístico
- Respuestas en español
- Contexto del usuario y de su viaje actual
- Soporte local con Ollama usando un modelo como `llama3.2:latest`

## Estructura del repositorio

```text
centro_viajero/
├── backend/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.*
├── docker-compose.yml
├── .env.example
├── README.md
└── .venv/
```

## Requisitos previos

Necesitarás lo siguiente antes de ejecutar el proyecto:

- Git
- Docker Desktop o Docker Engine
- Docker Compose
- Node.js 18+
- Python 3.11+
- Ollama instalado localmente para la IA del chatbot

## Credenciales demo

El proyecto viene con un usuario de prueba pre-cargado para facilitar el acceso inicial:

- Email: `juan@centro.viajero`
- Contraseña: `viajero123`

## Configuración inicial

### 1. Clonar el repositorio

```bash
git clone https://github.com/<tu-usuario>/centro_viajero.git
cd centro_viajero
```

### 2. Crear variables de entorno

Copia el ejemplo para configurar tu entorno local:

```bash
cp .env.example .env
```

El archivo .env.example contiene valores base para PostgreSQL y Ollama, por ejemplo:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=centro_viajero
DATABASE_URL=postgresql://postgres:postgres@db:5432/centro_viajero
JWT_SECRET=replace-with-a-long-random-secret
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

> Si vas a hacer despliegue real o compartir el proyecto, cambia `JWT_SECRET` por un valor seguro y no reutilices credenciales de prueba.

## Cómo ejecutar el proyecto

### Opción A: con Docker (recomendada)

```bash
docker compose up --build
```

Esto levanta:

- Base de datos PostgreSQL en `localhost:5432`
- Backend FastAPI en `http://localhost:8000`
- Frontend en `http://localhost:5173`
- Documentación Swagger en `http://localhost:8000/docs`

### Opción B: ejecución local sin Docker

#### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# o en Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

#### Ollama (chatbot)

Asegúrate de que Ollama esté ejecutándose localmente:

```bash
ollama serve
ollama pull llama3.2:latest
```

Luego inicia la app y prueba la conversación desde la pantalla de orientación.

## Verificar funcionamiento

### Frontend
- Abrir: `http://localhost:5173`
- Iniciar sesión con las credenciales demo

### Backend
- Swagger: `http://localhost:8000/docs`
- Root endpoint: `http://localhost:8000/`

### Chatbot
- Ir a la sección de orientación
- Enviar una consulta de viaje, por ejemplo: "¿Qué debo revisar antes de salir?"
- Si Ollama no está disponible, el backend cae a respuestas fallback, pero lo ideal es tenerlo corriendo localmente

## Pruebas

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

El proyecto incluye una prueba base para el chatbot en `backend/tests/test_chatbot.py`.

## Recomendaciones para forks

Si vas a hacer un fork del proyecto, te conviene seguir este flujo:

```bash
git clone https://github.com/<tu-usuario>/centro_viajero.git
cd centro_viajero

git remote rename origin upstream
git remote add origin https://github.com/<tu-usuario>/centro_viajero.git
git push -u origin main
```

Esto te deja:

- `upstream`: el repositorio original
- `origin`: tu fork personal

### Buenas prácticas al forkear

- Nunca subas secretos reales a GitHub
- Usa un `JWT_SECRET` distinto del ejemplo
- Mantén `.env` fuera del control de versiones
- Actualiza el proyecto con `git fetch upstream` y `git merge upstream/main` si quieres mantenerlo sincronizado

## Seguridad y producción

Antes de usarlo fuera de desarrollo:

- Cambia `JWT_SECRET`
- Usa credenciales reales y robustas para PostgreSQL
- No expongas la app sin HTTPS
- No uses modelos o endpoint de Ollama con configuración insegura
- Considera variables de entorno específicas por entorno (dev, staging, prod)

### Despliegue en VPS

El proyecto incluye una preparación base para despliegue en un servidor VPS. Consulta [DEPLOY_VPS.md](DEPLOY_VPS.md) y usa [scripts/deploy-vps.sh](scripts/deploy-vps.sh) para automatizar la instalación de Docker, firewall, certificados TLS y arranque de la app en producción.

### Seguridad de despliegue

Este repositorio incluye controles para reforzar la entrega a producción:

- CI/CD con validación automática: pruebas del backend, build del frontend y escaneo de integridad
- Análisis de dependencias: Dependabot + `pip-audit` + `npm audit`
- Escaneo de vulnerabilidades: revisión de secretos con Gitleaks
- Revisión manual antes de producción: el workflow `production-gate.yml` usa un entorno `production` que exige aprobación del responsable de despliegue
- Hardening: contenedores sin usuario root y política de actualización de dependencias

Se puede consultar la guía detallada en [SECURITY.md](SECURITY.md) y el procedimiento de patching en [PATCHING.md](PATCHING.md).

## Créditos y propósito

Este proyecto funciona como ejemplo de una plataforma inteligente para viajes, con una propuesta de producto enfocada en preparación, tranquilidad y asistencia para viajeros. Sirve como base para ampliar módulos como:

- reservas y pagos
- geolocalización
- recomendaciones por temporada
- notificaciones push
- integración con APIs externas de clima, vuelos o hoteles

## Contacto y contribución

Si quieres colaborar o adaptar el proyecto, puedes:

- crear ramas por funcionalidad
- mantener commits descriptivos
- documentar cambios relevantes para frontend, backend e IA

## Resumen ejecutivo

Centro Viajero es una plataforma completa para preparar un viaje de forma inteligente y ordenada. Está diseñada para ofrecer en una sola experiencia:

- preparación del viaje
- checklist personalizada
- contenido útil
- soporte de atención al viajero
- asistencia con IA local

Es un proyecto ideal para aprender arquitectura de frontend/backend, autenticación, integraciones con modelos locales y un flujo realista de producto digital de viajes.
