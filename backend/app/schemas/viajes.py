from datetime import date

from pydantic import BaseModel


class ViajeCreate(BaseModel):
    titulo: str
    destino: str
    fecha_inicio: date
    fecha_fin: date
    usuario_id: int = 1


class ViajeResponse(ViajeCreate):
    id: int
    estado: str

    model_config = {"from_attributes": True}