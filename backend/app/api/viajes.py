from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.dependencies import get_current_user, get_db
from ..models import Usuario, Viaje
from ..schemas.viajes import ViajeCreate, ViajeResponse

router = APIRouter(prefix="/viajes", tags=["viajes"])


@router.get('/', response_model=list[ViajeResponse])
def list_viajes(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Viaje).where(Viaje.usuario_id == current_user.id).order_by(Viaje.fecha_inicio)).all()


@router.post('/', response_model=ViajeResponse, status_code=201)
def create_viaje(payload: ViajeCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje = Viaje(**payload.model_dump(exclude={"usuario_id"}), usuario_id=current_user.id)
    db.add(viaje)
    db.commit()
    db.refresh(viaje)
    return viaje


@router.get('/{viaje_id}', response_model=ViajeResponse)
def get_viaje(viaje_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje = db.scalar(select(Viaje).where(Viaje.id == viaje_id, Viaje.usuario_id == current_user.id))
    if viaje is None:
        raise HTTPException(status_code=404, detail="Viaje no encontrado")
    return viaje
