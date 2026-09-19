import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.dependencies import get_current_user, get_db
from ..models import Tarea, Usuario, Viaje

router = APIRouter(prefix="/chatbot", tags=["chatbot"])
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)


class ChatMessageResponse(BaseModel):
    reply: str
    suggestions: list[str] = Field(default_factory=list)


def _build_user_context(db: Session, user: Usuario) -> dict:
    viaje = db.scalar(
        select(Viaje)
        .where(Viaje.usuario_id == user.id)
        .order_by(Viaje.fecha_inicio.asc())
    )

    if viaje is None:
        return {
            'usuario_nombre': user.nombre,
            'viaje': None,
            'tareas': [],
            'plan': [],
            'presupuesto_total': 0,
            'presupuesto_detallado': {},
            'tareas_pendientes': 0,
        }

    tareas = db.scalars(
        select(Tarea)
        .where(Tarea.viaje_id == viaje.id)
        .order_by(Tarea.id.asc())
    ).all()

    plan = viaje.plan or []
    presupuesto_detallado = viaje.presupuesto_detallado or {}

    return {
        'usuario_nombre': user.nombre,
        'viaje': {
            'titulo': viaje.titulo,
            'destino': viaje.destino,
            'estado': viaje.estado,
            'fecha_inicio': viaje.fecha_inicio.isoformat() if viaje.fecha_inicio else None,
            'fecha_fin': viaje.fecha_fin.isoformat() if viaje.fecha_fin else None,
            'clima_recomendado': viaje.clima_recomendado,
            'transporte_recomendado': viaje.transporte_recomendado,
            'descripcion': viaje.descripcion,
        },
        'plan': plan,
        'presupuesto_total': int(viaje.presupuesto_total or 0),
        'presupuesto_detallado': presupuesto_detallado,
        'tareas': [
            {'titulo': tarea.titulo, 'categoria': tarea.categoria, 'completada': tarea.completada}
            for tarea in tareas
        ],
        'tareas_pendientes': sum(1 for tarea in tareas if not tarea.completada),
    }


def _call_ollama(message: str, context: dict | None = None) -> str:
    system_prompt = (
        'Eres un asistente turístico de Centro Viajero. Responde en español, con lenguaje natural, claro y práctico. '
        'Usa el contexto del usuario y del viaje si existe, evita inventar datos y responde siempre con consejos útiles para viajar.'
    )

    prompt = message
    if context:
        viaje = context.get('viaje')
        tareas = context.get('tareas', [])
        plan = context.get('plan') or []
        presupuesto_total = context.get('presupuesto_total')
        presupuesto_detallado = context.get('presupuesto_detallado') or {}
        partes = [f"Usuario: {context.get('usuario_nombre', 'viajero')}"]
        if viaje:
            partes.append(
                f"Viaje actual: {viaje.get('titulo')} ({viaje.get('destino')}) | estado: {viaje.get('estado')} | fechas: {viaje.get('fecha_inicio')} a {viaje.get('fecha_fin')} | clima: {viaje.get('clima_recomendado')} | transporte: {viaje.get('transporte_recomendado')}"
            )
        if plan:
            primer_dia = plan[0]
            actividades = ', '.join((primer_dia.get('activities') or [])[:3])
            partes.append(f"Plan del viaje: Día {primer_dia.get('day', 1)} - {primer_dia.get('title')}. Actividades: {actividades}")
        if presupuesto_total:
            categorias = ', '.join(f"{k}: {v}" for k, v in list(presupuesto_detallado.items())[:3])
            partes.append(f"Presupuesto total: {presupuesto_total}; desglose: {categorias}")
        if tareas:
            pendientes = [t['titulo'] for t in tareas if not t.get('completada')]
            if pendientes:
                partes.append(f"Tareas pendientes: {', '.join(pendientes[:4])}")
        partes.append(f"Pregunta del usuario: {message}")
        prompt = '\n'.join(partes)

    payload = json.dumps({
        'model': OLLAMA_MODEL,
        'stream': False,
        'system': system_prompt,
        'prompt': prompt,
        'options': {'temperature': 0.3}
    }).encode('utf-8')
    request = Request(
        f'{OLLAMA_BASE_URL}/api/generate',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    with urlopen(request, timeout=90) as response:
        body = json.loads(response.read().decode('utf-8'))
    return body.get('response', '').strip()


def _build_reply(message: str, current_user: Usuario | None = None, context: dict | None = None) -> ChatMessageResponse:
    try:
        reply = _call_ollama(message, context)
        if reply:
            return ChatMessageResponse(
                reply=reply,
                suggestions=['Checklist de documentos', 'Qué llevar en la maleta', 'Seguridad y emergencia']
            )
    except (HTTPError, URLError, TimeoutError, ValueError, OSError):
        pass

    text = message.lower().strip()
    viaje = context.get('viaje') if context else None
    tareas_pendientes = context.get('tareas', []) if context else []
    pendientes = [item.get('titulo', 'Tarea pendiente') for item in tareas_pendientes if not item.get('completada', False)]
    plan = context.get('plan') if context else []
    presupuesto_total = context.get('presupuesto_total') if context else 0
    presupuesto_detallado = context.get('presupuesto_detallado') or {} if context else {}

    if context and context.get('viaje'):
        viaje = context['viaje']
        next_stage = (plan[0] if plan else None)
        if any(keyword in text for keyword in ['hoy', 'siguiente', 'próximo', 'proximo', 'qué hago', 'que hago', 'ahora']):
            if next_stage:
                activities = next_stage.get('activities') or []
                focus = activities[0] if activities else (pendientes[0] if pendientes else 'confirmar documentos')
                budget_hint = f"Tu presupuesto total es {presupuesto_total} COP." if presupuesto_total else 'Tu presupuesto está bien definido para esta etapa.'
                return ChatMessageResponse(
                    reply=f'Para hoy en {viaje["destino"]}, prioriza el día {next_stage.get("day", 1)}: {next_stage.get("title", "tu plan")}. Enfócate en {focus}. {budget_hint} Revisa también los gastos principales para que no se te salga la ruta de emergencia.',
                    suggestions=['Revisar presupuesto', 'Checklist del día', 'Qué hacer hoy']
                )

        if any(keyword in text for keyword in ['documento', 'pasaporte', 'visa', 'identidad', 'requisitos']):
            return ChatMessageResponse(
                reply=f'Para {viaje["titulo"]}, antes de salir revisa pasaporte, visa si aplica, seguro y copias digitales de cada documento. Si te quedan tareas como {pendientes[0] if pendientes else "confirmar reservas"}, priorízalas para reducir estrés antes del viaje. Tu plan actual del día {next_stage.get("day", 1) if next_stage else 1} ya te da una ruta útil para la preparación.',
                suggestions=['Checklist de documentos', 'Seguro de viaje', 'Documentos de viaje']
            )

        if any(keyword in text for keyword in ['maleta', 'equipaje', 'ropa', 'llevar', 'mochila']):
            focus = pendientes[0] if pendientes else 'confirmar transporte y alojamiento'
            return ChatMessageResponse(
                reply=f'Para tu viaje a {viaje["destino"]}, en la maleta pon ropa según el clima, calzado cómodo, medicinas, cargadores y una copia de tus documentos. También revisa {focus} para dejar la preparación más ordenada. Si quieres, hoy puedes seguir el plan del día {next_stage.get("day", 1) if next_stage else 1}.',
                suggestions=['Qué llevar en la maleta', 'Clima del destino', 'Preparación del equipaje']
            )

        if any(keyword in text for keyword in ['presupuesto', 'dinero', 'gasto', 'costo', 'coste', 'tarjeta', 'efectivo']):
            summary = ', '.join(f'{name}: {value}' for name, value in list(presupuesto_detallado.items())[:3]) or 'sin desglose aún'
            return ChatMessageResponse(
                reply=f'Tu presupuesto total para {viaje["destino"]} es {presupuesto_total} COP. El desglose principal es {summary}. Mantén ese margen para alojamiento, transporte y actividades para que el viaje se mantenga real y cómodo.',
                suggestions=['Revisar presupuesto', 'Control de gastos', 'Qué priorizar']
            )

    if any(keyword in text for keyword in ['documento', 'pasaporte', 'visa', 'identidad']):
        return ChatMessageResponse(
            reply='Antes de salir, revisa pasaporte, visa si aplica, seguro de viaje y copias digitales de cada documento importante. Guarda también la reserva y los datos de emergencia en tu móvil.',
            suggestions=['Checklist de documentos', 'Seguridad en ruta', 'Qué llevar en la maleta']
        )

    if any(keyword in text for keyword in ['maleta', 'equipaje', 'ropa', 'llevar', 'mochila']):
        return ChatMessageResponse(
            reply='Para la maleta, prioriza lo esencial: documentos, medicinas, cargadores, ropa por clima, calzado cómodo y una pequeña mochila para día a día. Si viajas con hijos o en temporada alta, revisa el pronóstico del destino.',
            suggestions=['Qué llevar según clima', 'Preparación del día de salida', 'Cómo organizar la maleta']
        )

    if any(keyword in text for keyword in ['clima', 'temperatura', 'ropa', 'pronostico']):
        return ChatMessageResponse(
            reply='Consulta el clima del destino 72 horas antes de salir. Si hay cambios bruscos, lleva capas, un abrigo ligero y calzado apropiado para caminar y para la noche.',
            suggestions=['Ropa por destino', 'Pronóstico del clima', 'Checklist de viaje']
        )

    if any(keyword in text for keyword in ['seguridad', 'emergencia', 'riesgo', 'medidas']):
        return ChatMessageResponse(
            reply='La seguridad suele mejorar cuando tienes un plan claro: guarda contactos de emergencia, comparte tu itinerario, revisa la zona de alojamiento y deja una copia de tus documentos con alguien de confianza.',
            suggestions=['Contactos útiles', 'Seguridad en alojamiento', 'Qué hacer ante un imprevisto']
        )

    if any(keyword in text for keyword in ['transporte', 'ruta', 'desplazamiento', 'bus', 'avion']):
        return ChatMessageResponse(
            reply='Organiza los traslados con tiempo. Confirma aeropuertos, horarios, conexiones y opciones de transporte local antes del día de salida para evitar retrasos innecesarios.',
            suggestions=['Cómo llegar al destino', 'Horario de salida', 'Transporte local']
        )

    if any(keyword in text for keyword in ['presupuesto', 'dinero', 'tarjeta', 'efectivo']):
        return ChatMessageResponse(
            reply='Mantén un presupuesto simple: reserva principal, pagos locales y un fondo para emergencias. Lleva una tarjeta y un poco de efectivo en la moneda del destino, además de la copia de respaldo en otro medio.',
            suggestions=['Presupuesto recomendado', 'Pagos y moneda', 'Costo del viaje']
        )

    if context and context.get('tareas_pendientes', 0):
        focus = pendientes[0] if pendientes else 'documentos y reservas'
        return ChatMessageResponse(
            reply=f'Veo que te quedan {context["tareas_pendientes"]} tareas pendientes antes del viaje. En este momento, prioriza {focus} para que la salida sea más tranquila.',
            suggestions=['Checklist de viaje', 'Tareas pendientes', 'Preparación del destino']
        )

    if viaje:
        return ChatMessageResponse(
            reply=f'Para tu próximo viaje a {viaje["destino"]}, te recomiendo organizar primero documentos, clima, transporte y reserva de alojamiento. Eso te da una salida más clara y con menos improvisación.',
            suggestions=['Checklist de documentos', 'Qué llevar en la maleta', 'Seguridad y emergencia']
        )

    return ChatMessageResponse(
        reply='Para viajar con más calma, te recomiendo organizar 4 cosas primero: documentos, reserva, clima y transporte. Si quieres, puedo ayudarte con un checklist específico según tu destino o tipo de viaje.',
        suggestions=['Checklist de documentos', 'Qué llevar en la maleta', 'Seguridad y emergencia']
    )


@router.post('/message', response_model=ChatMessageResponse)
def post_message(
    payload: ChatMessageRequest,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    context = _build_user_context(db, current_user)
    return _build_reply(payload.message, current_user=current_user, context=context)
