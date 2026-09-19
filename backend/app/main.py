import logging
import os
from collections import defaultdict, deque
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from time import monotonic

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .api import alertas, articulos, auth, chatbot, destinos, faqs, solicitudes, tareas, usuarios, viajes
from .core.security import build_security_headers, get_allowed_origins
from .db.init import initialize_database
from .monitoring import configure_logging, configure_sentry, record_http_request, render_metrics

configure_logging()
configure_sentry()
security_logger = logging.getLogger('centro_viajero.security')

rate_limit_store: defaultdict[str, deque[float]] = defaultdict(deque)
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
RATE_LIMIT_MAX_REQUESTS = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "120"))
ROUTE_RATE_LIMITS = {
    "/auth/login": {
        "window_seconds": int(os.getenv("RATE_LIMIT_LOGIN_WINDOW_SECONDS", "600")),
        "max_requests": int(os.getenv("RATE_LIMIT_LOGIN_MAX_REQUESTS", "5")),
    },
    "/chatbot/message": {
        "window_seconds": int(os.getenv("RATE_LIMIT_CHATBOT_WINDOW_SECONDS", "60")),
        "max_requests": int(os.getenv("RATE_LIMIT_CHATBOT_MAX_REQUESTS", "20")),
    },
}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    initialize_database()
    yield


app = FastAPI(title="Centro Viajero API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    route = request.url.path
    route_limits = ROUTE_RATE_LIMITS.get(route)
    if route_limits:
        limit_key = f"{route}:{client_ip}"
        timestamps = rate_limit_store[limit_key]
        now = monotonic()
        while timestamps and now - timestamps[0] > route_limits["window_seconds"]:
            timestamps.popleft()

        if len(timestamps) >= route_limits["max_requests"]:
            security_logger.warning("rate_limit_hit route=%s client_ip=%s", route, client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests for this endpoint. Please wait and retry later."},
            )

        timestamps.append(now)
    else:
        timestamps = rate_limit_store[f"global:{client_ip}"]
        now = monotonic()
        while timestamps and now - timestamps[0] > RATE_LIMIT_WINDOW_SECONDS:
            timestamps.popleft()

        if len(timestamps) >= RATE_LIMIT_MAX_REQUESTS:
            security_logger.warning("global_rate_limit_hit client_ip=%s", client_ip)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please wait before retrying."},
            )

        timestamps.append(now)

    response = await call_next(request)

    if response.status_code in {401, 403, 429}:
        security_logger.warning(
            "security_event method=%s path=%s status=%s client_ip=%s",
            request.method,
            route,
            response.status_code,
            client_ip,
        )
    else:
        security_logger.info(
            "request_event method=%s path=%s status=%s client_ip=%s",
            request.method,
            route,
            response.status_code,
            client_ip,
        )

    record_http_request(request.method, route, response.status_code)

    for key, value in build_security_headers().items():
        response.headers.setdefault(key, value)

    response.headers.setdefault("x-ratelimit-limit", str(route_limits["max_requests"] if route_limits else RATE_LIMIT_MAX_REQUESTS))
    return response


@app.get('/metrics')
def metrics_route() -> Response:
    return Response(content=render_metrics(), media_type='text/plain; version=0.7.0')


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(viajes.router)
app.include_router(destinos.router)
app.include_router(articulos.router)
app.include_router(faqs.router)
app.include_router(tareas.router)
app.include_router(alertas.router)
app.include_router(solicitudes.router)
app.include_router(chatbot.router)

@app.get('/')
def root():
    return {"message": "Centro Viajero API", "status": "ready"}
