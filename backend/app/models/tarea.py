from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

from ..db.base import Base


class Tarea(Base):
    __tablename__ = "tareas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    completada = Column(Boolean, nullable=False, default=False)
    viaje_id = Column(Integer, ForeignKey("viajes.id"), nullable=False, index=True)