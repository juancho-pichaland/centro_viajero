from fastapi.testclient import TestClient

from app.api import chatbot
from app.main import app

client = TestClient(app)


def test_chatbot_returns_contextual_reply(monkeypatch):
    fake_user = type('User', (), {'id': 1, 'nombre': 'Juan García', 'email': 'juan@centro.viajero'})()
    monkeypatch.setattr(chatbot, '_build_user_context', lambda db, user: {'usuario_nombre': user.nombre, 'viaje': {'titulo': 'Ruta por el Eje Cafetero', 'destino': 'Colombia', 'estado': 'En preparación'}, 'tareas': [{'titulo': 'Confirmar alojamiento', 'completada': False}], 'tareas_pendientes': 1})
    monkeypatch.setattr(chatbot, '_call_ollama', lambda message, context=None: 'Antes de salir revisa tu pasaporte, visa y seguro de viaje.')

    app.dependency_overrides[chatbot.get_current_user] = lambda: fake_user
    app.dependency_overrides[chatbot.get_db] = lambda: None
    try:
        response = client.post('/chatbot/message', json={'message': '¿Qué documentos necesito para viajar?'})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert 'reply' in body
    assert isinstance(body['reply'], str)
    assert len(body['reply']) > 10


def test_chatbot_mentions_trip_destination_in_fallback(monkeypatch):
    fake_user = type('User', (), {'id': 1, 'nombre': 'Juan García', 'email': 'juan@centro.viajero'})()
    context = {
        'usuario_nombre': 'Juan García',
        'viaje': {
            'titulo': 'Ruta por Medellín',
            'destino': 'Medellín',
            'estado': 'En preparación',
            'fecha_inicio': '2026-09-21',
            'fecha_fin': '2026-09-27'
        },
        'tareas': [
            {'titulo': 'Confirmar alojamiento', 'completada': False},
            {'titulo': 'Comprar seguro', 'completada': False}
        ],
        'tareas_pendientes': 2,
    }
    monkeypatch.setattr(chatbot, '_build_user_context', lambda db, user: context)
    monkeypatch.setattr(chatbot, '_call_ollama', lambda message, context=None: '')

    app.dependency_overrides[chatbot.get_current_user] = lambda: fake_user
    app.dependency_overrides[chatbot.get_db] = lambda: None
    try:
        response = client.post('/chatbot/message', json={'message': '¿Qué debo llevar en la maleta?'})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert 'Medellín' in body['reply']
    assert 'maleta' in body['reply'].lower()


def test_chatbot_uses_plan_and_budget_in_next_steps(monkeypatch):
    fake_user = type('User', (), {'id': 1, 'nombre': 'Juan García', 'email': 'juan@centro.viajero'})()
    context = {
        'usuario_nombre': 'Juan García',
        'viaje': {
            'titulo': 'Ruta por Cartagena',
            'destino': 'Cartagena',
            'estado': 'En preparación',
            'fecha_inicio': '2026-10-10',
            'fecha_fin': '2026-10-15'
        },
        'plan': [
            {'day': 1, 'title': 'Llegada y alojamiento', 'activities': ['Confirmar check-in', 'Revisar transporte local']},
            {'day': 2, 'title': 'Centro histórico', 'activities': ['Recorrer museo', 'Reservar tour']}
        ],
        'presupuesto_total': 1800000,
        'presupuesto_detallado': {'hospedaje': 700000, 'transporte': 350000},
        'tareas': [
            {'titulo': 'Confirmar alojamiento', 'completada': False},
            {'titulo': 'Reservar tour', 'completada': True}
        ],
        'tareas_pendientes': 1,
    }
    monkeypatch.setattr(chatbot, '_build_user_context', lambda db, user: context)
    monkeypatch.setattr(chatbot, '_call_ollama', lambda message, context=None: '')

    app.dependency_overrides[chatbot.get_current_user] = lambda: fake_user
    app.dependency_overrides[chatbot.get_db] = lambda: None
    try:
        response = client.post('/chatbot/message', json={'message': '¿Qué hago hoy antes de salir?'})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert 'día' in body['reply'].lower()
    assert 'presupuesto' in body['reply'].lower() or 'hospedaje' in body['reply'].lower()
