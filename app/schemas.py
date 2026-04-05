from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


# Auth schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    telegram_chat_id: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    telegram_chat_id: Optional[str] = None
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
    last_temp: Optional[float] = None
    last_condition: Optional[str] = None
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True