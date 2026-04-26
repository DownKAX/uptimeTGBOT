import asyncio
from unittest.mock import patch

import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from alembic import command
from alembic.config import Config
from main import app

import os


# Переделать под новую аутентификацию

@pytest_asyncio.fixture(name='client')
async def async_client():
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope='class', autouse=True)
async def alembic_test_data_seeding():
    config = Config('alembic_test.ini')
    await asyncio.to_thread(command.upgrade, config, 'head')
    yield
    await asyncio.to_thread(command.downgrade, config, '819b67f4bd63')

@pytest_asyncio.fixture(scope='function', name='redis_mock')
async def redis_mocking():
    from redis.asyncio import Redis as AsyncRedis
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    client = AsyncRedis(host=redis_host, port=6379, db=3, decode_responses=True)
    await client.flushdb()
    yield client


class TestRegister:
    @pytest.mark.asyncio
    async def test_success_signup_and_login(self, client, redis_mock):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password1234',
                'email': 'test_user@mail.ru', 'telegram_id': 1234567890}

        # Привязываем redis_mock к текущему циклу
        await bring_redis_in_same_loop(redis_mock, asyncio.get_running_loop())

        async def fake_redis():
            return redis_mock

        with patch('app.auth.register.get_async_redis', new=fake_redis):
            response = await client.post("auth/signup", data=data) # Для записи кода подтверждения в redis
            redis_data = await redis_mock.hgetall(data.get('email'))
            verification_code = int(iter(redis_data.keys()).__next__())

            # adding user
            loging_in = await client.post("auth/email_verification", data={'email_code': verification_code})
            assert 'username' in loging_in.json()

    @pytest.mark.asyncio
    async def test_password_do_not_match(self, client):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password12346',
                'email': 'test_user@mail.ru', 'telegram_id': 1234567890}
        response = await client.post("auth/signup", data=data)
        assert response.json()['detail'][0]['msg'] == 'Value error, Passwords do not match'
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_short_password(self, client):
        data = {'username': 'human2', 'password': 'test', 'password_confirmation': 'test',
                'email': 'test_user@mail.ru', 'telegram_id': 1234567890}
        response = await client.post("auth/signup", data=data)
        assert response.json()['detail'][0]['msg'] == 'Value error, Password len must be between 8 and 64'
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_long_password(self, client):
        data = {'username': 'human2', 'password': 'test' * 40, 'password_confirmation': 'test' * 40,
                'email': 'test_user@mail.ru', 'telegram_id': 1234567890}
        response = await client.post("auth/signup", data=data)
        assert response.json()['detail'][0]['msg'] == 'Value error, Password len must be between 8 and 64'
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_name_taken(self, client):
        data = {'username': 'user1', 'password': 'testtesttest', 'password_confirmation': 'testtesttest',
                'email': 'test_user@mail.ru', 'telegram_id': 1234567890}
        response = await client.post("auth/signup", data=data)
        assert response.json()['detail'] == 'Username already exists'
        assert response.status_code == 409

async def bring_redis_in_same_loop(redis_mock, loop):
    if hasattr(redis_mock, 'connection_pool'):
        for conn in redis_mock.connection_pool._available_connections:
            if hasattr(conn, '_writer'):
                conn._writer._transport._loop = loop
