import random
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    id : int | None = None
    username: str
    password: str
    email: EmailStr
    telegram_id: int
    register_time: datetime = Field(default_factory=lambda: datetime.now())

class Url(BaseModel):
    id: int | None = None
    url: str
    time_added_seconds: int = Field(default_factory=lambda: random.randint(0, 59))#Field(default_factory=lambda: datetime.now().second)
    used_by_counter: int = 1
    status: str = "UP"

class UserUrl(BaseModel):
    user_id: int
    url_id: int

class JoinedUserUrl(BaseModel):
    user_id: int
    url_id: int
    url: str
