from types import SimpleNamespace

from fastapi import HTTPException
from starlette.requests import Request

from app.core import security
from app.db.dependencies import require_roles, resolve_token_from_request
from app.monitoring import configure_logging, get_metrics_snapshot, record_http_request


def test_get_allowed_origins_sanitizes_csv_values():
    origins = security.get_allowed_origins('http://localhost:5173, https://app.example.com ,  http://127.0.0.1:5173')

    assert origins == ['http://localhost:5173', 'https://app.example.com', 'http://127.0.0.1:5173']


def test_build_security_headers_includes_hardening_values():
    headers = security.build_security_headers()

    assert headers['x-frame-options'] == 'DENY'
    assert headers['x-content-type-options'] == 'nosniff'
    assert 'strict-transport-security' in headers
    assert 'content-security-policy' in headers


def test_refresh_tokens_include_expiration_metadata():
    token = security.create_refresh_token(42, expires_days=1)
    user_id = security.decode_refresh_token(token)

    assert user_id == 42
    assert security.JWT_REFRESH_EXPIRE_DAYS >= 1


def test_resolve_token_from_request_uses_cookie_value_when_header_missing():
    request = Request({
        'type': 'http',
        'method': 'GET',
        'path': '/usuarios/me/dashboard',
        'headers': [(b'cookie', b'access_token=abc123')],
    })

    assert resolve_token_from_request(request) == 'abc123'


def test_require_roles_rejects_non_admin_user():
    admin_user = SimpleNamespace(rol='admin')
    traveler_user = SimpleNamespace(rol='traveler')

    allowed = require_roles('admin')
    assert allowed(admin_user).rol == 'admin'

    try:
        require_roles('admin')(traveler_user)
        assert False, 'Expected forbidden role access'
    except HTTPException as exc:
        assert exc.status_code == 403


def test_monitoring_supports_logging_and_metrics():
    config = configure_logging()
    record_http_request('GET', '/health', 200)
    record_http_request('POST', '/auth/login', 401)
    snapshot = get_metrics_snapshot()

    assert config['version'] == 1
    assert snapshot['http_requests_total'] >= 2
    assert snapshot['http_errors_total'] >= 1
