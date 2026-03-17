import hashlib
import secrets
import json
from fastapi import HTTPException

import bcrypt
from fastapi import APIRouter, Request, Response, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import user_dependency
from app.auth.exceptions import InvalidPasswordException, ExpiredAccessToken, InvalidRefreshToken
from app.auth.models import RegistrationForm, User, Tokens
from app.auth.redis_repository import get_data_from_redis
from app.auth.security import verification_stamp, get_jwt_tokens, validate_access_token, check_session
from redis_client import get_async_redis

auth = APIRouter(prefix="/auth")

@auth.post('/signup')
async def register(response: Response, credentials: RegistrationForm = Form(...)):
    password_bytes: bytes = credentials.password.encode('utf-8')
    hashed_password: bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    user_data = json.dumps({'username': credentials.username, 'password': hashed_password.decode(), 'telegram_id': credentials.telegram_id})

    #email code section
    code = str(secrets.randbelow(100000000)).zfill(8)
    temp_id = secrets.token_urlsafe(8)
    response.set_cookie(key='temp_id', value=temp_id, httponly=True, max_age=360)

    r = await get_async_redis()
    temp_id_count = await r.hlen(credentials.email)
    if temp_id_count > 5:
        raise HTTPException(429, detail='You tried to register more than 5 times, try again later')
    await r.hsetex(name=credentials.email, mapping={code: user_data}, ex=360)
    await r.setex(name=temp_id, value=json.dumps([credentials.email, code]), time=360)

    await r.rpush('email_codes_for_worker', json.dumps({credentials.email: code})) # worker будет забирать отсюда

    return {'detail': 'Code send to email'}

@auth.post('/email_verification')
async def check_email_code(user_service: user_dependency, request: Request,  email_code: str = Form(...)):
    r = await get_async_redis()
    temp_id = request.cookies.get('temp_id')
    signup_data = await r.get(temp_id)
    user_mail, code_linked_to_temp_id = json.loads(signup_data)
    if code_linked_to_temp_id == email_code:
        user_data = await r.hget(user_mail, email_code)
        user = User(email=user_mail, **json.loads(user_data))

        await r.hdel(user_mail, email_code)
        await r.delete(temp_id)
        data = await user_service.add_one_user(user)
        return data
    else:
        raise HTTPException(400, detail='Invalid verification code')


@auth.post('/login')
async def log_in(user_service: user_dependency, response: Response, credentials: OAuth2PasswordRequestForm = Depends()):
    user: User = await user_service.select_one_user(username = credentials.username)
    if not bcrypt.checkpw(credentials.password.encode("utf-8"), user.password.encode()):
        raise InvalidPasswordException
    await verification_stamp(user.username, response)
    return user

@auth.post("check_token")
async def check_token(request: Request, response: Response) -> dict:
    tokens: Tokens = await get_jwt_tokens(request)
    try:
        payload: dict = await validate_access_token(tokens.access_token)
    except ExpiredAccessToken:
        tokens: Tokens = await update_tokens(request, response)
        payload: dict = await validate_access_token(tokens.access_token)
    return payload

@auth.post('/new_tokens')
async def update_tokens(request: Request, response: Response) -> Tokens:
    tokens: Tokens = await get_jwt_tokens(request)
    hashed_refresh_token = hashlib.sha256(tokens.refresh_token.encode()).hexdigest()
    data_from_redis: dict = await get_data_from_redis(hashed_refresh_token)
    if data_from_redis:
        await check_session(request, data_from_redis['fingerprint'])
        tokens: Tokens = await verification_stamp(data_from_redis['username'], response)
        return tokens
    else:
        raise InvalidRefreshToken
