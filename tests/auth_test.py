import asyncio

import pytest
from httpx import AsyncClient, ASGITransport
import pytest_asyncio
from alembic import command
from alembic.config import Config
from main import app

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

class TestRegister:
    @pytest.mark.asyncio
    async def test_success_signup(self, client):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password1234'}
        response = await client.post("auth/signup", data=data)
        assert 'username' in response.json()
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_password_do_not_match(self, client):
        data = {'username': 'human2', 'password': 'password1234', 'password_confirmation': 'password12534'}
        response = await client.post("auth/signup", data=data)
        assert response.json()['detail'][0]['msg'] == 'Value error, Passwords do not match'
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_short_password(self, client):
        data = {'username': 'human2', 'password': 'pass', 'password_confirmation': 'pass'}
        response = await client.post("auth/signup", data=data)
        assert response.json()['detail'][0]['msg'] == 'Value error, Password len must be between 8 and 64'
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_long_password(self, client):
        data = {'username': 'human2', 'password': 'pass' * 40, 'password_confirmation': 'pass' * 40}
        response = await client.post("auth/signup", data=data)
        assert response.json()['detail'][0]['msg'] == 'Value error, Password len must be between 8 and 64'
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_name_taken(self, client):
        data = {'username': 'user1', 'password': 'password1234', 'password_confirmation': 'password1234'}
        response = await client.post("auth/signup", data=data)
        print(response.json())
        assert response.json()['detail'] == 'Some data is not unique, try something else'
        assert response.status_code == 409
