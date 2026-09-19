from sqlalchemy import JSON, Column, Date, ForeignKey, Integer, String
from ..db.base import Base


class Viaje(Base):
    __tablename__ = 'viajes'
    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    descripcion = Column(String, nullable=True, default='')
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    estado = Column(String, nullable=False, default='En preparación')
    clima_recomendado = Column(String, nullable=False, default='Templado')
    transporte_recomendado = Column(String, nullable=False, default='Aéreo + transporte local')
    presupuesto_total = Column(Integer, nullable=False, default=0)
    presupuesto_detallado = Column(JSON, nullable=False, default=dict)
    dias_recomendados = Column(JSON, nullable=False, default=list)
    plan = Column(JSON, nullable=False, default=list)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'), nullable=False, index=True)
