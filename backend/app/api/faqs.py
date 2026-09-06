from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db.dependencies import get_db
from ..models import FAQ
from ..schemas.informacion import FAQResponse

router = APIRouter(prefix="/faqs", tags=["faqs"])


@router.get('/', response_model=list[FAQResponse])
def list_faqs(q: str | None = None, db: Session = Depends(get_db)):
    query = select(FAQ).order_by(FAQ.id)
    if q:
        query = query.where(FAQ.pregunta.ilike(f"%{q}%"))
    return db.scalars(query).all()