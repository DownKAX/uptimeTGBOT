from aiogram import types
from aiogram.fsm.context import FSMContext

from app.telegram_bot.keyboards.common_keyboards import сrud_markup


async def registration_required(message: types.Message):
    await message.answer("Вы не зарегистрированы в нашей системе, пройдите регистрацию, чтобы получить доступ")

async def start_handler(message: types.Message):
    await message.answer('Привет, можно добавить ресурсы для мониторинга доступности', reply_markup=сrud_markup)

async def back_handler(callback_data: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback_data.message.answer('Вы вернулись назад, что делаем дальше?', reply_markup=сrud_markup)
    await callback_data.answer()