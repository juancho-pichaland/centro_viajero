from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class ViajeCreate(BaseModel):
    titulo: str
    destino: str
    descripcion: str | None = None
    fecha_inicio: date
    fecha_fin: date
    estado: str = 'En preparación'
    clima_recomendado: str = 'Templado'
    transporte_recomendado: str = 'Aéreo + transporte local'
    presupuesto_total: int = 0
    presupuesto_detallado: dict[str, Any] = Field(default_factory=dict)
    dias_recomendados: list[str] = Field(default_factory=list)
    plan: list[dict[str, Any]] = Field(default_factory=list)
    usuario_id: int = 1


class ViajeUpdate(BaseModel):
    titulo: str | None = None
    destino: str | None = None
    descripcion: str | None = None
    fecha_inicio: date | None = None
    fecha_fin: date | None = None
    estado: str | None = None
    clima_recomendado: str | None = None
    transporte_recomendado: str | None = None
    presupuesto_total: int | None = None
    presupuesto_detallado: dict[str, Any] | None = None
    dias_recomendados: list[str] | None = None
    plan: list[dict[str, Any]] | None = None


class ViajeResponse(ViajeCreate):
    id: int
    model_config = {"from_attributes": True}