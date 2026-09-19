import logging
from datetime import datetime

logger = logging.getLogger('centro_viajero.audit')


def log_audit_event(action: str, user_id: int | None = None, details: dict | None = None) -> None:
    payload = {
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'action': action,
        'user_id': user_id,
        'details': details or {},
    }
    logger.info('audit_event=%s', payload)
