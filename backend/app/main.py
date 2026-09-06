from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import alertas, articulos, auth, chatbot, destinos, faqs, solicitudes, tareas, usuarios, viajes
from .db.init import initialize_database

app = FastAPI(title="Centro Viajero API")


@app.on_event("startup")
def startup() -> None:
    initialize_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(viajes.router)
app.include_router(destinos.router)
app.include_router(articulos.router)
app.include_router(faqs.router)
app.include_router(tareas.router)
app.include_router(alertas.router)
app.include_router(solicitudes.router)
app.include_router(chatbot.router)

@app.get('/')
def root():
    return {"message": "Centro Viajero API", "status": "ready"}
