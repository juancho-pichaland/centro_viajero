from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.dependencies import get_db
from ..models import Destino
from ..schemas.informacion import DestinoResponse

router = APIRouter(prefix="/destinos", tags=["destinos"])


@router.get('/', response_model=list[DestinoResponse])
def list_destinos(q: str | None = None, db: Session = Depends(get_db)):
    query = select(Destino).order_by(Destino.nombre)
    if q:
        query = query.where(Destino.nombre.ilike(f"%{q}%"))
    return db.scalars(query).all()
