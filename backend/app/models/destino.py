from sqlalchemy import Column, Integer, String

from ..db.base import Base


class Destino(Base):
    __tablename__ = "destinos"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    pais = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
