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
