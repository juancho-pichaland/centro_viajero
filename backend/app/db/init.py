from datetime import date

from sqlalchemy import select, text

from .base import Base
from .session import SessionLocal, engine
from ..core.security import hash_password
from ..models import Articulo, Destino, FAQ, Tarea, Usuario, Viaje


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE destinos ADD COLUMN IF NOT EXISTS pais VARCHAR NOT NULL DEFAULT 'Colombia'"))
        connection.execute(text("ALTER TABLE articulos ADD COLUMN IF NOT EXISTS resumen VARCHAR NOT NULL DEFAULT ''"))
        connection.execute(text("ALTER TABLE articulos ADD COLUMN IF NOT EXISTS categoria VARCHAR NOT NULL DEFAULT 'General'"))
        connection.execute(text("ALTER TABLE articulos ADD COLUMN IF NOT EXISTS destino_id INTEGER"))
    with SessionLocal() as db:
        user = db.scalar(select(Usuario).where(Usuario.email == "juan@centro.viajero"))
        if user is None:
            user = Usuario(
                nombre="Juan García",
                email="juan@centro.viajero",
                password_hash=hash_password("viajero123"),
            )
            db.add(user)
            db.flush()

        trip = db.scalar(select(Viaje).where(Viaje.usuario_id == user.id))
        if trip is None:
            trip = Viaje(
                titulo="Ruta por el Eje Cafetero",
                destino="Colombia",
                fecha_inicio=date(2026, 10, 12),
                fecha_fin=date(2026, 10, 20),
                usuario_id=user.id,
            )
            db.add(trip)
            db.flush()
            db.add_all([
                Tarea(titulo="Verificar documentos de identidad", categoria="Documentos", completada=True, viaje_id=trip.id),
                Tarea(titulo="Confirmar alojamiento", categoria="Reservas", viaje_id=trip.id),
                Tarea(titulo="Preparar seguro de viaje", categoria="Seguridad", viaje_id=trip.id),
                Tarea(titulo="Consultar recomendaciones del destino", categoria="Información", viaje_id=trip.id),
            ])
        if db.scalar(select(Destino.id).limit(1)) is None:
            eje = Destino(nombre="Eje Cafetero", pais="Colombia", descripcion="Montañas, pueblos cafeteros y paisajes verdes para viajar con calma.")
            cartagena = Destino(nombre="Cartagena de Indias", pais="Colombia", descripcion="Historia, arquitectura caribeña y recomendaciones para recorrer la ciudad.")
            db.add_all([eje, cartagena])
            db.flush()
            db.add_all([
                Articulo(titulo="Documentos esenciales para tu viaje", resumen="Organiza tus documentos antes de salir y evita contratiempos.", contenido="Revisa tu documento de identidad, reservas, pasajes y copias digitales. Guarda una copia offline para consultarla sin conexión.", categoria="Preparación"),
                Articulo(titulo="Cómo preparar tu equipaje", resumen="Una maleta ligera empieza con una lista bien pensada.", contenido="Consulta el clima, elige prendas versátiles y deja espacio para artículos de uso diario. Lleva siempre una pequeña bolsa para documentos.", categoria="Equipaje"),
                Articulo(titulo="Moverte por el Eje Cafetero", resumen="Consejos para planear traslados entre pueblos y fincas.", contenido="Calcula tiempos entre destinos y confirma los horarios de transporte con anticipación. Las rutas pueden cambiar en temporada de lluvias.", categoria="Destino", destino_id=eje.id),
                Articulo(titulo="Viajar con tranquilidad", resumen="Hábitos simples para cuidar tu seguridad durante el viaje.", contenido="Comparte tu itinerario, mantén tus documentos protegidos y usa canales oficiales para reservas y solicitudes.", categoria="Seguridad"),
            ])
            db.add_all([
                FAQ(pregunta="¿Qué documentos debo revisar antes de viajar?", respuesta="Revisa tu documento de identidad, reservas, pasajes y cualquier requisito especial del destino.", categoria="Documentos"),
                FAQ(pregunta="¿Cómo puedo organizar mi checklist?", respuesta="Abre Checklist desde el menú y marca cada tarea cuando la completes. El progreso se guarda automáticamente.", categoria="Preparación"),
                FAQ(pregunta="¿Dónde encuentro recomendaciones del destino?", respuesta="En Centro de información puedes buscar artículos y consultar las preguntas frecuentes.", categoria="Información"),
                FAQ(pregunta="¿Qué hago si necesito ayuda personalizada?", respuesta="Registra una solicitud desde Solicitudes para que el equipo pueda orientarte.", categoria="Soporte"),
            ])
        db.commit()