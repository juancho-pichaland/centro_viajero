from pydantic import BaseModel


class DestinoResponse(BaseModel):
    id: int
    nombre: str
    pais: str
    descripcion: str | None = None

    model_config = {"from_attributes": True}


class ArticuloResponse(BaseModel):
    id: int
    titulo: str
    resumen: str
    contenido: str
    categoria: str
    destino_id: int | None = None

    model_config = {"from_attributes": True}


class FAQResponse(BaseModel):
    id: int
    pregunta: str
    respuesta: str
    categoria: str

    model_config = {"from_attributes": True}