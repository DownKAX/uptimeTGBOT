import hashlib, hmac

from app.auth.models import RefreshData
from app.core.settings import settings
from redis_client import get_async_redis

async def add_session(session: RefreshData):
    r = await get_async_redis()

    hashed_fingerprint = hmac.new(
        settings.FINGERPRINT_SECRET.encode(),
        session.fingerprint.encode(),
        hashlib.sha256).hexdigest()
    hashed_refresh_token = hashlib.sha256(session.refresh_token.encode()).hexdigest()

    await r.hset(hashed_refresh_token, mapping={'fingerprint': hashed_fingerprint, 'username': session.username})
    await r.expire(hashed_refresh_token, settings.REFRESH_TOKEN_EXPIRATION * 24 * 60 * 60)

async def get_data_from_redis(client_hashed_refresh_token: str) -> dict:
    r = await get_async_redis()
    data: dict = await r.hgetall(client_hashed_refresh_token)
    return {"fingerprint": data['fingerprint'], "username": data['username']}

