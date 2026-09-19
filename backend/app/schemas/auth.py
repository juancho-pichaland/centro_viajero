from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    nombre: str
    rol: str = 'traveler'


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    rol: str = 'traveler'

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str
    user: UserResponse