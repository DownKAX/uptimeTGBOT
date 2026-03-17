import hashlib
import hmac

import jwt
import secrets

from fastapi import Response, Request
from datetime import timedelta, datetime, UTC

from app.core.settings import settings
from app.auth.models import RefreshData, Tokens
from app.auth.exceptions import TokenNotFound, InvalidAccessToken, ExpiredAccessToken, UserCompromisation
from app.auth.redis_repository import add_session


async def create_access_token(username: str):
    data = {"username": username, "exp": datetime.now(UTC) + timedelta(hours=settings.ACCESS_TOKEN_EXPIRATION)}
    token = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

async def create_refresh_token() -> str:
    refresh_token = secrets.token_urlsafe(64)
    return refresh_token

async def create_fingerprint() -> str:
    fingerprint = secrets.token_urlsafe(32)
    return fingerprint

async def create_session(username) -> RefreshData:
    refresh_token = await create_refresh_token()
    fingerprint = await create_fingerprint()

    data = RefreshData(
        username=username,
        fingerprint=fingerprint,
        refresh_token=refresh_token
    )
    return data

async def validate_access_token(token: str) -> dict:
    if token is None:
        raise TokenNotFound
    try:
        payload: dict = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ExpiredAccessToken
    except jwt.InvalidTokenError:
        raise InvalidAccessToken

async def check_session(request, fingerprint_from_redis: str):
    user_fingerprint = hmac.new(
        settings.FINGERPRINT_SECRET.encode(),
        request.cookies.get("fingerprint").encode(),
        hashlib.sha256).hexdigest()
    if not hmac.compare_digest(fingerprint_from_redis, user_fingerprint):
        raise UserCompromisation()

async def set_jwt_tokens(tokens: Tokens, response: Response):
    response.set_cookie(key="token", value=tokens.access_token)
    response.set_cookie(key="refresh_token", value=tokens.refresh_token)
    return response

async def get_jwt_tokens(request: Request) -> Tokens:
    access_token = request.cookies.get("token")
    refresh_token = request.cookies.get("refresh_token")
    return Tokens(access_token=access_token, refresh_token=refresh_token)

async def set_fingerprint(fingerprint, response: Response):
    response.set_cookie(key="fingerprint", value=fingerprint, secure=True, httponly=True)

async def verification_stamp(username: str, response: Response):
    access_token: str = await create_access_token(username)
    session: RefreshData = await create_session(username)

    await set_fingerprint(session.fingerprint, response)
    await set_jwt_tokens(tokens=Tokens(access_token=access_token, refresh_token=session.refresh_token), response=response)

    await add_session(session)
    return Tokens(access_token=access_token, refresh_token=session.refresh_token)