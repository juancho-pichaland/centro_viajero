from sqlalchemy import Column, Integer, String, Text

from ..db.base import Base


class Articulo(Base):
    __tablename__ = "articulos"
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    resumen = Column(String, nullable=False)
    contenido = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    destino_id = Column(Integer, nullable=True)

