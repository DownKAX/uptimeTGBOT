from aiogram import types

async def registration_required(message: types.Message):
    await message.answer("Вы не зарегистрированы в нашей системе, пройдите регистрацию, чтобы получить доступ")