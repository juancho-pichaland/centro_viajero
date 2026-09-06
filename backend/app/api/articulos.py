from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..db.dependencies import get_db
from ..models import Articulo
from ..schemas.informacion import ArticuloResponse

router = APIRouter(prefix="/articulos", tags=["articulos"])


@router.get('/', response_model=list[ArticuloResponse])
def list_articulos(q: str | None = None, categoria: str | None = None, db: Session = Depends(get_db)):
    query = select(Articulo).order_by(Articulo.id.desc())
    if q:
        query = query.where(or_(Articulo.titulo.ilike(f"%{q}%"), Articulo.resumen.ilike(f"%{q}%")))
    if categoria:
        query = query.where(Articulo.categoria == categoria)
    return db.scalars(query).all()
