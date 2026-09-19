import logging
import logging.config
import os


def configure_logging() -> dict:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            }
        },
        "root": {
            "handlers": ["console"],
            "level": level,
        },
    }
    logging.config.dictConfig(config)
    return config


HTTP_METRICS = {
    "http_requests_total": 0,
    "http_errors_total": 0,
}


def record_http_request(method: str, path: str, status_code: int) -> None:
    HTTP_METRICS["http_requests_total"] += 1
    if status_code >= 400:
        HTTP_METRICS["http_errors_total"] += 1


def get_metrics_snapshot() -> dict[str, int]:
    return dict(HTTP_METRICS)


def render_metrics() -> str:
    lines = [
        "# HELP centro_viajero_http_requests_total Total HTTP requests received by the API.",
        "# TYPE centro_viajero_http_requests_total counter",
        f"centro_viajero_http_requests_total {HTTP_METRICS['http_requests_total']}",
        "# HELP centro_viajero_http_errors_total Total HTTP errors returned by the API.",
        "# TYPE centro_viajero_http_errors_total counter",
        f"centro_viajero_http_errors_total {HTTP_METRICS['http_errors_total']}",
    ]
    return "\n".join(lines) + "\n"


def configure_sentry() -> bool:
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return False

    try:
        import sentry_sdk
    except ImportError:
        return False

    sentry_sdk.init(
        dsn=dsn,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        environment=os.getenv("APP_ENV", "development"),
        send_default_pii=False,
    )
    return True
