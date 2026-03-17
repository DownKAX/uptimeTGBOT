from fastapi import APIRouter, Depends, Form

from app.api.endpoints.dependencies import user_dependency
from app.auth.models import User
from app.auth.register import check_token
from app.repositories.models import ColumnValue

user_router = APIRouter(prefix='/user')

@user_router.post('/create_data')
async def create_user(user_service: user_dependency, user: User):
    added_data = await user_service.add_one_user(user)
    return added_data

@user_router.get('/read_data')
async def get_all_users(example_service: user_dependency):
    data = await example_service.select_all_users()
    return {'data': data}

@user_router.delete('/delete_data')
async def delete_user(example_service: user_dependency, id: int = Form(...)):
    deleted_data = await example_service.delete_data_by_id(id)
    return deleted_data

@user_router.patch('/update_data')
async def update_users (example_service: user_dependency, column_and_value: ColumnValue = Form(...), values: dict = Form(...)):
    updated_data = await example_service.update_one_user(column_and_value, values)
    return updated_data

@user_router.get('/test_tokens')
async def get_test_tokens(user: dict = Depends(check_token)):
    return {"message": "success"}