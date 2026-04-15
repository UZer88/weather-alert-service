from datetime import datetime

from pydantic import BaseModel, EmailStr


# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    telegram_chat_id: str | None = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    telegram_chat_id: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Subscription schemas
class SubscriptionCreate(BaseModel):
    city: str


class SubscriptionResponse(BaseModel):
    id: int
    city: str
    last_temp: float | None = None
    last_condition: str | None = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
