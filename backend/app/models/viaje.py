from sqlalchemy import Column, Date, ForeignKey, Integer, String
from ..db.base import Base


class Viaje(Base):
    __tablename__ = 'viajes'
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String, nullable=False, default="En preparación")
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
