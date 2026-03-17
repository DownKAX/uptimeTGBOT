from datetime import datetime

from pydantic import BaseModel, Field, model_validator, EmailStr

from app.auth.exceptions import TokenNotFound


class User(BaseModel):
    username: str
    password: str
    email: EmailStr
    telegram_id: int
    register_time: datetime = Field(default_factory=lambda: datetime.now())

class RefreshData(BaseModel):
    username: str
    fingerprint: str
    refresh_token: str

class RegistrationForm(BaseModel):
    username: str
    password: str
    password_confirmation: str
    email: EmailStr
    telegram_id: int
    register_time: datetime = Field(default_factory=lambda: datetime.now())

    @model_validator(mode='after')
    def validate_and_hash(self):
        if 4 > (l :=len(self.username)) or l > 20:
            raise ValueError('Username must be between 4 and 20 characters')
        if 8 > (l := len(self.password)) or l > 64:
            raise ValueError('Password len must be between 8 and 64')
        if self.password != self.password_confirmation:
            raise ValueError('Passwords do not match')

        del self.password_confirmation
        return self

class Tokens(BaseModel):
    access_token: str
    refresh_token: str

    @model_validator(mode='before')
    def token_existence(self):
        if not (self["access_token"]) or (not self["refresh_token"]):
            raise TokenNotFound
        return self

