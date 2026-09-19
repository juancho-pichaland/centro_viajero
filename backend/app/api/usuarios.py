import csv
import io

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..core.audit import log_audit_event
from ..db.dependencies import get_db, get_current_user, require_roles
from ..models import Tarea, Usuario, Viaje
from ..schemas.auth import UserResponse

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


def _budget_status_for_trip(trip) -> str:
    breakdown = getattr(trip, 'presupuesto_detallado', {}) or {}
    if isinstance(breakdown, dict):
        spent_total = sum(float(value) for value in breakdown.values() if isinstance(value, (int, float)))
    elif isinstance(breakdown, (list, tuple)):
        spent_total = sum(
            float(item.get('monto', 0)) if isinstance(item, dict) else 0.0
            for item in breakdown
        )
    else:
        spent_total = 0.0
    budget_total = float(getattr(trip, 'presupuesto_total', 0) or 0)
    if budget_total <= 0:
        return 'within_budget'
    if spent_total <= budget_total * 0.75:
        return 'within_budget'
    if spent_total <= budget_total * 1.05:
        return 'watching_budget'
    return 'over_budget'


def _readiness_for_trip(trip, trip_tasks) -> int:
    if trip is None:
        return 0
    completed_tasks = sum(1 for task in trip_tasks if getattr(task, 'completada', False))
    total_tasks = len(trip_tasks)
    completion_ratio = completed_tasks / total_tasks if total_tasks else 0.0
    trip_fields = [
        getattr(trip, 'titulo', None),
        getattr(trip, 'destino', None),
        getattr(trip, 'descripcion', None),
        getattr(trip, 'fecha_inicio', None),
        getattr(trip, 'fecha_fin', None),
        getattr(trip, 'plan', None),
    ]
    filled_fields = sum(1 for value in trip_fields if value not in (None, '', [], {}, False))
    readiness = int(round((completion_ratio * 70) + ((filled_fields / len(trip_fields)) * 30)))
    return max(0, min(100, readiness))


def build_user_dashboard(user: Usuario, db: Session) -> dict:
    trip = db.scalar(
        select(Viaje)
        .where(Viaje.usuario_id == user.id)
        .order_by(Viaje.id.desc())
    )
    trip_tasks = []
    trip_id = getattr(trip, 'id', None)
    if trip is not None and trip_id is not None:
        trip_tasks = list(
            db.scalars(
                select(Tarea)
                .where(Tarea.viaje_id == trip_id)
                .order_by(Tarea.id)
            ).all()
        )
    elif trip is not None:
        trip_tasks = list(getattr(trip, 'tareas', []) or [])

    completed_tasks = sum(1 for task in trip_tasks if getattr(task, 'completada', False))
    total_tasks = len(trip_tasks)
    readiness = _readiness_for_trip(trip, trip_tasks) if trip is not None else 35
    budget_status = _budget_status_for_trip(trip) if trip is not None else 'within_budget'

    next_focus = 'Aún no tienes un viaje activo configurado.'
    if trip_tasks:
        pending_task = next((task.titulo for task in trip_tasks if not getattr(task, 'completada', False)), None)
        if pending_task:
            next_focus = pending_task
        else:
            next_focus = 'Tu plan está preparado y listo para revisión final.'
    elif trip is not None:
        next_focus = 'Define las tareas clave del itinerario para activar la preparación del viaje.'

    return {
        'nombre': user.nombre,
        'email': user.email,
        'trip_destino': getattr(trip, 'destino', None),
        'trip_titulo': getattr(trip, 'titulo', None),
        'trip_estado': getattr(trip, 'estado', None),
        'travel_readiness_score': readiness,
        'budget_status': budget_status,
        'next_focus': next_focus,
        'completed_tasks': completed_tasks,
        'total_tasks': total_tasks,
        'active_trip_exists': trip is not None,
    }


def build_operations_summary(db: Session) -> dict:
    users = list(db.scalars(select(Usuario)).all())
    trips = list(db.scalars(select(Viaje)).all())
    tasks = list(db.scalars(select(Tarea)).all())
    task_map = {}
    for task in tasks:
        viaje_id = getattr(task, 'viaje_id', None)
        if viaje_id is not None:
            task_map.setdefault(viaje_id, []).append(task)

    readiness_scores = []
    budget_alerts = 0
    active_trips = 0
    focus_candidates = []

    for trip in trips:
        trip_tasks = task_map.get(getattr(trip, 'id', None), [])
        readiness_scores.append(_readiness_for_trip(trip, trip_tasks))
        if str(getattr(trip, 'estado', '')).lower() not in {'completado', 'cancelado', 'cancelada'}:
            active_trips += 1
        if _budget_status_for_trip(trip) in {'watching_budget', 'over_budget'}:
            budget_alerts += 1

        pending = next(
            (getattr(task, 'titulo', 'Tarea pendiente') for task in trip_tasks if not getattr(task, 'completada', False)),
            None,
        )
        if pending:
            focus_candidates.append(pending)

    average_readiness = round(sum(readiness_scores) / len(readiness_scores)) if readiness_scores else 0
    next_focus = focus_candidates[0] if focus_candidates else 'Sin tareas pendientes en este momento'
    chart_data = [
        {'label': 'Preparación', 'value': average_readiness, 'color': '#7ad7b1'},
        {'label': 'Viajes activos', 'value': min(100, round((active_trips / max(1, len(trips))) * 100)) if trips else 0, 'color': '#7fa7ff'},
        {'label': 'Alertas', 'value': min(100, budget_alerts * 25), 'color': '#f0c574'},
        {'label': 'Usuarios', 'value': min(100, round((len(users) / max(1, len(users) + 2)) * 100)), 'color': '#d7d4ff'},
    ]

    return {
        'total_usuarios': len(users),
        'total_viajes': len(trips),
        'viajes_activos': active_trips,
        'promedio_preparacion': average_readiness,
        'presupuesto_total': sum(float(getattr(trip, 'presupuesto_total', 0) or 0) for trip in trips),
        'alertas_presupuesto': budget_alerts,
        'budget_alerts': budget_alerts,
        'foco_principal': next_focus,
        'estado_general': 'estable' if average_readiness >= 70 else 'revisión',
        'chart_data': chart_data,
    }


def build_admin_overview(db: Session) -> dict:
    users = list(db.scalars(select(Usuario)).all())
    trips = list(db.scalars(select(Viaje)).all())
    traveler_ids = {user.id for user in users if getattr(user, 'rol', 'traveler') == 'traveler'}
    travelers_with_trip = len({trip.usuario_id for trip in trips if getattr(trip, 'usuario_id', None) in traveler_ids})
    average_readiness = 0
    if trips:
        readiness = []
        for trip in trips:
            task_list = list(db.scalars(select(Tarea).where(Tarea.viaje_id == trip.id)).all())
            readiness.append(_readiness_for_trip(trip, task_list))
        average_readiness = round(sum(readiness) / len(readiness))

    if average_readiness >= 80:
        report_status = 'healthy'
    elif average_readiness >= 55:
        report_status = 'monitoring'
    else:
        report_status = 'attention'

    return {
        'admin_count': sum(1 for user in users if getattr(user, 'rol', 'traveler') == 'admin'),
        'traveler_count': sum(1 for user in users if getattr(user, 'rol', 'traveler') == 'traveler'),
        'travelers_with_trip': travelers_with_trip,
        'active_trips': sum(1 for trip in trips if str(getattr(trip, 'estado', '')).lower() not in {'completado', 'cancelado', 'cancelada'}),
        'report_status': report_status,
        'permissions': {
            'manage_travelers': True,
            'review_reports': True,
            'edit_budget': True,
            'approve_changes': True,
        },
    }


def build_business_report(db: Session) -> dict:
    summary = build_operations_summary(db)
    users = {user.id: user for user in db.scalars(select(Usuario)).all()}
    trips = list(db.scalars(select(Viaje)).all())
    tasks = list(db.scalars(select(Tarea)).all())
    task_map = {}
    for task in tasks:
        viaje_id = getattr(task, 'viaje_id', None)
        if viaje_id is not None:
            task_map.setdefault(viaje_id, []).append(task)

    csv_rows = []
    for trip in trips:
        traveler = users.get(getattr(trip, 'usuario_id', None))
        trip_tasks = task_map.get(getattr(trip, 'id', None), [])
        completed_tasks = sum(1 for task in trip_tasks if getattr(task, 'completada', False))
        budget_status = _budget_status_for_trip(trip)
        csv_rows.append({
            'usuario': getattr(traveler, 'nombre', 'Sin usuario'),
            'email': getattr(traveler, 'email', ''),
            'destino': getattr(trip, 'destino', ''),
            'estado': getattr(trip, 'estado', ''),
            'presupuesto_total': float(getattr(trip, 'presupuesto_total', 0) or 0),
            'alerta_presupuesto': budget_status in {'watching_budget', 'over_budget'},
            'readiness_score': _readiness_for_trip(trip, trip_tasks),
            'tareas_completadas': completed_tasks,
            'tareas_total': len(trip_tasks),
        })

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=['usuario', 'email', 'destino', 'estado', 'presupuesto_total', 'alerta_presupuesto', 'readiness_score', 'tareas_completadas', 'tareas_total'],
    )
    writer.writeheader()
    writer.writerows(csv_rows)

    return {
        'summary': summary,
        'csv_rows': csv_rows,
        'csv_content': output.getvalue(),
    }


@router.get('/', response_model=list[UserResponse])
def list_usuarios(db: Session = Depends(get_db)):
    return db.scalars(select(Usuario).order_by(Usuario.id)).all()


@router.get('/me/dashboard')
def get_user_dashboard(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_user_dashboard(current_user, db)


@router.get('/operaciones/summary')
def get_operations_summary(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return build_operations_summary(db)


@router.get('/admin/overview')
def get_admin_overview(current_user: Usuario = Depends(require_roles('admin')), db: Session = Depends(get_db)):
    log_audit_event('admin_overview_viewed', current_user.id, {'user_role': current_user.rol})
    return build_admin_overview(db)


@router.get('/admin/report')
def get_admin_report(current_user: Usuario = Depends(require_roles('admin')), db: Session = Depends(get_db)):
    report = build_business_report(db)
    log_audit_event('admin_report_exported', current_user.id, {'rows': len(report.get('csv_rows', []))})
    return report
