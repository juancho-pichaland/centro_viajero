from fastapi import APIRouter

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post('/message')
def post_message():
    return {"reply": "placeholder"}
