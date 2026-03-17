import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from alembic import command
from alembic.config import Config
from main import app
import asyncio

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

class TestLogin:
    @pytest.mark.asyncio
    async def test_login_success(self, client):
        data = {'username': 'user', 'password': 'user1234'}
        response = await client.post('/auth/login', data=data)
        assert response.status_code == 200
        assert "username" in response.json()

    @pytest.mark.asyncio
    async def test_login_failure(self, client):
        data = {'username': 'user1', 'password': 'user1235'}
        response = await client.post('/auth/login', data=data)
        assert response.status_code == 401
        assert response.json()['detail'] == 'Invalid password!'

    @pytest.mark.asyncio
    async def test_login_user_not_exist(self, client):
        data = {'username': 'user12331', 'password': '12456777888'}
        response = await client.post('/auth/login', data=data)
        assert response.status_code == 401
        assert response.json()['detail'] == 'User does not exist'