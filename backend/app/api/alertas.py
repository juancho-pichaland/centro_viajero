from fastapi import APIRouter

router = APIRouter(prefix="/alertas", tags=["alertas"])


@router.get('/')
def list_alertas():
    return {"alertas": []}
