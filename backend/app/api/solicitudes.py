from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.audit import log_audit_event
from ..db.dependencies import get_current_user, get_db
from ..models import Solicitud, Usuario
from ..schemas.solicitudes import SolicitudCreate, SolicitudResponse

router = APIRouter(prefix="/solicitudes", tags=["solicitudes"])


@router.get('/', response_model=list[SolicitudResponse])
def list_solicitudes(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Solicitud).where(Solicitud.usuario_id == current_user.id).order_by(Solicitud.creada_en.desc())).all()


@router.post('/', response_model=SolicitudResponse, status_code=201)
def create_solicitud(payload: SolicitudCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    solicitud = Solicitud(**payload.model_dump(), usuario_id=current_user.id)
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    log_audit_event('request_created', current_user.id, {'request_id': solicitud.id, 'category': solicitud.categoria, 'priority': solicitud.prioridad})
    return solicitud


@router.get('/{solicitud_id}', response_model=SolicitudResponse)
def get_solicitud(solicitud_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    solicitud = db.scalar(select(Solicitud).where(Solicitud.id == solicitud_id, Solicitud.usuario_id == current_user.id))
    if solicitud is None:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return solicitud
