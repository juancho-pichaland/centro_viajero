from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.dependencies import get_current_user, get_db
from ..models import Usuario, Viaje
from ..schemas.viajes import ViajeCreate, ViajeResponse, ViajeUpdate

router = APIRouter(prefix="/viajes", tags=["viajes"])


def default_destination_profile(destino: str) -> dict[str, Any]:
    normalized = (destino or 'Colombia').lower()
    if 'medell' in normalized:
        return {
            'clima_recomendado': 'Templado y fresco',
            'transporte_recomendado': 'Bus intermunicipal + transporte local',
            'presupuesto_total': 1400000,
            'presupuesto_detallado': {'hospedaje': 550000, 'transporte': 250000, 'alimentacion': 300000, 'actividades': 300000},
            'dias_recomendados': ['Día 1: llegada y descanso', 'Día 2: pueblos y cafés', 'Día 3: rutas verdes y cultura'],
        }
    if 'cartagena' in normalized:
        return {
            'clima_recomendado': 'Cálido y húmedo',
            'transporte_recomendado': 'Transporte urbano + tours cortos',
            'presupuesto_total': 1800000,
            'presupuesto_detallado': {'hospedaje': 700000, 'transporte': 350000, 'alimentacion': 250000, 'actividades': 300000},
            'dias_recomendados': ['Día 1: centro histórico', 'Día 2: playas y muelles', 'Día 3: recorrido cultural'],
        }
    if 'bogot' in normalized or 'cali' in normalized:
        return {
            'clima_recomendado': 'Medio y variable',
            'transporte_recomendado': 'Metro / bus + traslado puntual',
            'presupuesto_total': 1100000,
            'presupuesto_detallado': {'hospedaje': 450000, 'transporte': 200000, 'alimentacion': 250000, 'actividades': 200000},
            'dias_recomendados': ['Día 1: llegada y plan urbano', 'Día 2: cultura y gastronomía', 'Día 3: cierre del recorrido'],
        }
    return {
        'clima_recomendado': 'Variable según temporada',
        'transporte_recomendado': 'Traslado principal + movilidad local',
        'presupuesto_total': 900000,
        'presupuesto_detallado': {'hospedaje': 350000, 'transporte': 180000, 'alimentacion': 220000, 'actividades': 150000},
        'dias_recomendados': ['Día 1: llegada y ajuste', 'Día 2: plan principal', 'Día 3: cierre de la experiencia'],
    }


def normalize_budget_breakdown(breakdown: dict[str, Any] | None) -> dict[str, int]:
    if not breakdown:
        return {}

    normalized: dict[str, int] = {}
    for key, value in breakdown.items():
        if isinstance(value, str):
            cleaned = value.replace('$', '').replace('.', '').replace(',', '').replace(' ', '')
            numeric = int(float(cleaned)) if cleaned else 0
        else:
            numeric = int(value)
        normalized[str(key)] = numeric
    return normalized


def normalize_plan(plan_data: list[dict[str, Any]] | None, destino: str) -> list[dict[str, Any]]:
    fallback = build_default_plan(destino)
    if not plan_data:
        return fallback

    normalized: list[dict[str, Any]] = []
    for index, stage in enumerate(plan_data, start=1):
        if not isinstance(stage, dict):
            continue
        activities = stage.get('activities') or stage.get('tasks') or []
        if isinstance(activities, str):
            activities = [activities]
        stage_payload = {
            'day': int(stage.get('day') or index),
            'title': str(stage.get('title') or stage.get('name') or f'Etapa {index}'),
            'summary': str(stage.get('summary') or stage.get('detail') or 'Revisa la logística del día.'),
            'activities': [str(item) for item in activities if str(item).strip()],
            'destination': destino,
        }
        normalized.append(stage_payload)

    return normalized or fallback


def build_default_plan(destino: str) -> list[dict[str, Any]]:
    base = (destino or 'Colombia').strip() or 'Colombia'
    stages = [
        {
            'day': 1,
            'title': f'Preparación para {base}',
            'summary': 'Revisa documentos, traslados y confirmación de alojamiento antes del viaje.',
            'activities': ['Confirmar reserva', 'Revisar documentos', 'Guardar contactos de emergencia'],
        },
        {
            'day': 2,
            'title': 'Ruta principal del destino',
            'summary': 'Organiza la primera jornada según clima, transporte y zonas recomendadas.',
            'activities': ['Confirmar transporte local', 'Definir puntos de interés', 'Revisar horarios de recorrido'],
        },
        {
            'day': 3,
            'title': 'Cierre del plan',
            'summary': 'Deja margen para actividad libre y revisión final del presupuesto.',
            'activities': ['Revisar gastos', 'Confirmar salida', 'Guardar copias digitales'],
        },
    ]
    if 'Medellín' in base:
        stages[1]['summary'] = 'Medellín reclama rutas cortas, clima templado y movimientos suaves entre el centro y las zonas verdes.'
        stages[1]['activities'] = ['Confirmar traslados entre barrios', 'Usar calzado cómodo para caminar', 'Reservar experiencia principal del día']
    elif 'Cartagena' in base:
        stages[1]['summary'] = 'Cartagena combina historia, clima cálido y recorridos cortos. Planea movilidad con margen para calor y caminatas.'
        stages[1]['activities'] = ['Confirmar traslado desde el aeropuerto', 'Definir la ruta del centro histórico', 'Reservar una actividad de playa o muelle']
    elif 'Bogotá' in base or 'Cali' in base:
        stages[1]['summary'] = 'Ajusta el recorrido por logística urbana, clima variable y actividades de día completo.'
        stages[1]['activities'] = ['Revisar hora pico', 'Definir zonas a visitar', 'Preparar efectivo para transporte local']
    for stage in stages:
        stage['destination'] = base
    return [
        {
            'day': int(stage.get('day', index + 1)),
            'title': stage['title'],
            'summary': stage['summary'],
            'activities': list(stage.get('activities') or []),
            'destination': base,
        }
        for index, stage in enumerate(stages)
    ]


def calculate_budget_summary(trip: dict[str, Any]) -> dict[str, Any]:
    budget = normalize_budget_breakdown(trip.get('presupuesto_detallado') or {})
    total = int(trip.get('presupuesto_total') or sum(budget.values()))
    used = sum(budget.values())
    return {
        'total': total,
        'categories': budget,
        'used': used,
        'remaining': max(total - used, 0),
    }


def _normalize_trip_payload(payload: ViajeCreate | ViajeUpdate | dict, current_user: Usuario) -> dict[str, Any]:
    data = payload.model_dump(exclude_none=True) if hasattr(payload, 'model_dump') else dict(payload)
    data.pop('usuario_id', None)
    destino = data.get('destino') or 'Colombia'
    default_profile = default_destination_profile(destino)
    data['presupuesto_detallado'] = normalize_budget_breakdown(data.get('presupuesto_detallado') or default_profile.get('presupuesto_detallado', {}))
    data['plan'] = normalize_plan(data.get('plan'), destino)
    if not data.get('clima_recomendado'):
        data['clima_recomendado'] = default_profile.get('clima_recomendado', 'Templado')
    if not data.get('transporte_recomendado'):
        data['transporte_recomendado'] = default_profile.get('transporte_recomendado', 'Aéreo + transporte local')
    if not data.get('presupuesto_total'):
        data['presupuesto_total'] = default_profile.get('presupuesto_total', 0)
    if not data.get('dias_recomendados'):
        data['dias_recomendados'] = default_profile.get('dias_recomendados', [])
    if not data.get('descripcion'):
        data['descripcion'] = f'Plan general para {destino}. Revisa documentos, presupuesto y transporte antes de salir.'
    data['usuario_id'] = current_user.id
    return data


@router.get('/', response_model=list[ViajeResponse])
def list_viajes(current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Viaje).where(Viaje.usuario_id == current_user.id).order_by(Viaje.fecha_inicio)).all()


@router.post('/', response_model=ViajeResponse, status_code=201)
def create_viaje(payload: ViajeCreate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje_data = _normalize_trip_payload(payload, current_user)
    viaje = Viaje(**viaje_data)
    db.add(viaje)
    db.commit()
    db.refresh(viaje)
    return viaje


@router.get('/{viaje_id}', response_model=ViajeResponse)
def get_viaje(viaje_id: int, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje = db.scalar(select(Viaje).where(Viaje.id == viaje_id, Viaje.usuario_id == current_user.id))
    if viaje is None:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')
    return viaje


@router.patch('/{viaje_id}', response_model=ViajeResponse)
def update_viaje(viaje_id: int, payload: ViajeUpdate, current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje = db.scalar(select(Viaje).where(Viaje.id == viaje_id, Viaje.usuario_id == current_user.id))
    if viaje is None:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')

    updates = payload.model_dump(exclude_none=True)
    if updates.get('destino'):
        profile = default_destination_profile(updates['destino'])
        updates.setdefault('clima_recomendado', profile['clima_recomendado'])
        updates.setdefault('transporte_recomendado', profile['transporte_recomendado'])
        updates.setdefault('presupuesto_total', profile['presupuesto_total'])
        updates.setdefault('presupuesto_detallado', profile['presupuesto_detallado'])
        updates.setdefault('dias_recomendados', profile['dias_recomendados'])
        updates.setdefault('plan', build_default_plan(updates['destino']))

    if 'presupuesto_detallado' in updates:
        updates['presupuesto_detallado'] = normalize_budget_breakdown(updates['presupuesto_detallado'])
    if 'plan' in updates:
        updates['plan'] = normalize_plan(updates['plan'], updates.get('destino') or viaje.destino)

    for field, value in updates.items():
        setattr(viaje, field, value)

    db.commit()
    db.refresh(viaje)
    return viaje


@router.patch('/{viaje_id}/plan', response_model=ViajeResponse)
def update_travel_plan(viaje_id: int, payload: dict[str, Any], current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje = db.scalar(select(Viaje).where(Viaje.id == viaje_id, Viaje.usuario_id == current_user.id))
    if viaje is None:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')

    plan = normalize_plan(payload.get('plan') or viaje.plan or build_default_plan(viaje.destino), viaje.destino)
    viaje.plan = plan
    if payload.get('dias_recomendados'):
        viaje.dias_recomendados = payload['dias_recomendados']
    if payload.get('descripcion'):
        viaje.descripcion = payload['descripcion']
    if payload.get('destino'):
        viaje.destino = payload['destino']
        viaje.plan = normalize_plan(plan, viaje.destino)
    db.commit()
    db.refresh(viaje)
    return viaje


@router.patch('/{viaje_id}/budget', response_model=ViajeResponse)
def update_trip_budget(viaje_id: int, payload: dict[str, Any], current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje = db.scalar(select(Viaje).where(Viaje.id == viaje_id, Viaje.usuario_id == current_user.id))
    if viaje is None:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')

    if 'presupuesto_detallado' in payload:
        viaje.presupuesto_detallado = normalize_budget_breakdown(payload['presupuesto_detallado'])
    if 'presupuesto_total' in payload:
        viaje.presupuesto_total = int(payload['presupuesto_total'])
    db.commit()
    db.refresh(viaje)
    return viaje


@router.post('/{viaje_id}/plan', response_model=ViajeResponse)
def replace_travel_plan(viaje_id: int, payload: dict[str, Any], current_user: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    viaje = db.scalar(select(Viaje).where(Viaje.id == viaje_id, Viaje.usuario_id == current_user.id))
    if viaje is None:
        raise HTTPException(status_code=404, detail='Viaje no encontrado')

    plan = normalize_plan(payload.get('plan') or build_default_plan(viaje.destino), viaje.destino)
    viaje.plan = plan
    viaje.presupuesto_detallado = normalize_budget_breakdown(payload.get('presupuesto_detallado', viaje.presupuesto_detallado or {}))
    viaje.presupuesto_total = int(payload.get('presupuesto_total', viaje.presupuesto_total or 0))
    viaje.clima_recomendado = payload.get('clima_recomendado', viaje.clima_recomendado)
    viaje.transporte_recomendado = payload.get('transporte_recomendado', viaje.transporte_recomendado)
    viaje.dias_recomendados = payload.get('dias_recomendados', viaje.dias_recomendados or [])
    viaje.descripcion = payload.get('descripcion', viaje.descripcion or '')
    db.commit()
    db.refresh(viaje)
    return viaje
