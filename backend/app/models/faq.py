from sqlalchemy import Column, Integer, String, Text

from ..db.base import Base


class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    pregunta = Column(String, nullable=False)
    respuesta = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)