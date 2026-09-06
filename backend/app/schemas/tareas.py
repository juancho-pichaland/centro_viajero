from pydantic import BaseModel


class TareaResponse(BaseModel):
    id: int
    titulo: str
    categoria: str
    completada: bool
    viaje_id: int

    model_config = {"from_attributes": True}