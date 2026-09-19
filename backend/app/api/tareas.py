from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.audit import log_audit_event
from ..db.dependencies import get_current_user, get_db
from ..models import Tarea, Usuario, Viaje
from ..schemas.tareas import TareaResponse

router = APIRouter(prefix="/tareas", tags=["tareas"])


@router.get('/', response_model=list[TareaResponse])
def list_tareas(current_user: Usuario = Depends(get_current_user), viaje_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Tarea).join(Viaje).where(Viaje.usuario_id == current_user.id)
    if viaje_id is not None:
        query = query.where(Tarea.viaje_id == viaje_id)
    return db.scalars(query.order_by(Tarea.id)).all()


@router.patch('/{tarea_id}', response_model=TareaResponse)
def toggle_tarea(tarea_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    tarea = db.scalar(select(Tarea).join(Viaje).where(Tarea.id == tarea_id, Viaje.usuario_id == current_user.id))
    if tarea is None:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    tarea.completada = not tarea.completada
    db.commit()
    db.refresh(tarea)
    log_audit_event('task_toggled', current_user.id, {'task_id': tarea.id, 'completed': tarea.completada})
    return tarea
