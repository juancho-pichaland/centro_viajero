from datetime import datetime

from pydantic import BaseModel, Field


class SolicitudCreate(BaseModel):
    asunto: str = Field(min_length=5, max_length=160)
    descripcion: str = Field(min_length=10, max_length=4000)
    categoria: str = Field(min_length=2, max_length=80)
    prioridad: str = "Normal"


class SolicitudResponse(SolicitudCreate):
    id: int
    estado: str
    respuesta: str | None = None
    creada_en: datetime

    model_config = {"from_attributes": True}