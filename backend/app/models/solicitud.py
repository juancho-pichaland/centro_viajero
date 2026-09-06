from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from ..db.base import Base


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id = Column(Integer, primary_key=True, index=True)
    asunto = Column(String, nullable=False)
    descripcion = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    prioridad = Column(String, nullable=False, default="Normal")
    estado = Column(String, nullable=False, default="Pendiente")
    respuesta = Column(Text, nullable=True)
    creada_en = Column(DateTime, nullable=False, default=datetime.utcnow)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)