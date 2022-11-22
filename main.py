from aiogram import Bot, Dispatcher, executor, types 
from config import token 


bot = Bot(token = token)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"Здраствуйте, {message.from_user.full_name}. Чем могу помочь?")

executor.start_polling(dp)