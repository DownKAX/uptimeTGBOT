from sqlalchemy.exc import IntegrityError, NoResultFound
from fastapi import HTTPException

def common_validation(FuncException, e_code):
    async def wrapper(func, *args, e_message: str = None, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except FuncException:
            raise HTTPException(status_code=e_code, detail=e_message)
    return wrapper

unique_validation = common_validation(IntegrityError, e_code=409)
exists_validation = common_validation(NoResultFound, e_code=401)