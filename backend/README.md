# Backend - Centro Viajero

Este directorio contiene la API principal del proyecto. Está construida con FastAPI y sigue una arquitectura modular por dominio, con separación de rutas, modelos, esquemas y lógica de base de datos.

## Objetivo

El backend expone la lógica de negocio de la aplicación y se encarga de:

- autenticar usuarios
- gestionar viajes y checklist
- administrar contenido informativo
- registrar solicitudes de soporte
- integrar un asistente turístico con Ollama

## Estructura principal

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── main.py
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

## Dependencias principales

- FastAPI
- SQLAlchemy
- PostgreSQL driver
- Pydantic
- PyJWT
- pytest

## Variables de entorno

Crea un archivo `.env` o usa la configuración del proyecto con Docker. Los valores recomendados son:

```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/centro_viajero
JWT_SECRET=replace-with-a-long-random-secret
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:latest
```

## Ejecutar localmente

### Con entorno virtual

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Con Docker

```bash
cd ..
docker compose up --build backend
```

## Endpoints relevantes

La API incluye rutas como:

- `/auth/register`
- `/auth/login`
- `/usuarios`
- `/viajes`
- `/tareas`
- `/solicitudes`
- `/chatbot/message`

Puedes explorarlos en la documentación interactiva:

```text
http://localhost:8000/docs
```

## Chatbot

El endpoint principal del chatbot es:

```http
POST /chatbot/message
```

Ejemplo de cuerpo:

```json
{
  "message": "¿Qué debo revisar antes de salir?"
}
```

El backend intenta consultar Ollama para responder con contexto del usuario y del viaje actual. Si la IA no está disponible, devuelve una respuesta fallback útil.

## Base de datos

La inicialización ocurre al arrancar la aplicación. Si la base de datos no existe, el sistema crea tablas y añade datos demo como:

- usuario de prueba
- viaje de ejemplo
- checklist inicial
- artículos y FAQs

## Pruebas

```bash
cd backend
pytest -q
```

## Recomendaciones para forks

Si haces fork del proyecto, mantén este flujo:

```bash
git remote rename origin upstream
git remote add origin https://github.com/<tu-usuario>/centro_viajero.git
git push -u origin main
```

Y asegúrate de:

- usar un secreto JWT propio
- no subir `.env` con información real
- mantener actualizadas las dependencias y la configuración local

## Nota

Este backend sirve como base para una aplicación de preparación de viajes con IA local, aunque puede ampliarse fácilmente a integraciones con clima, reservas, geolocalización, boletines o alertas personalizadas.
