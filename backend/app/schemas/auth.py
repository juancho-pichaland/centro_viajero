from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(LoginRequest):
    nombre: str


class UserResponse(BaseModel):
    id: int
    nombre: str
    email: EmailStr

    model_config = {"from_attributes": True}


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse