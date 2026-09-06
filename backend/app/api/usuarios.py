from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.dependencies import get_db
from ..models import Usuario
from ..schemas.auth import UserResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get('/', response_model=list[UserResponse])
def list_usuarios(db: Session = Depends(get_db)):
    return db.scalars(select(Usuario).order_by(Usuario.id)).all()
