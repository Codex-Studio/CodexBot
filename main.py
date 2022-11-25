from aiogram import Bot, Dispatcher, executor, types 
import config
import psycopg2
import logging
import os

bot = Bot(token = config.token)
dp = Dispatcher(bot)
connect = psycopg2.connect(
    user = config.DATABASE_USER,
    password = config.DATABASE_USER_PASSWORD,
    database = config.DATABASE_NAME,
    host = config.DATABASE_HOST,
)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"Здраствуйте, {message.from_user.full_name}. Чем могу помочь?")

@dp.message_handler(commands=['contact'])
async def send_contacts(message: types.Message):
    cursor = connect.cursor()
    cursor.execute(f"SELECT id_telegram FROM users_user;")
    result = cursor.fetchall()
    for user in result:
        if message.from_user.id in user:
            cur = connect.cursor()
            cur.execute(f"SELECT id, name, email, phone, subject, status FROM settings_contact;")
            result = cur.fetchall()
            print(result)
            if result:
                for i in result:
                    res = "".join(list(str(i))).replace(",", "").replace("'", "").replace("(", "").replace(")", "")
                    with open('contact.txt', 'a+') as contact:
                        if 'False' in res:
                            contact.write(f"{res}\n")
                        else:
                            await message.answer("Нет текущих контактов")
                with open('contact.txt', 'r') as contact:
                    try:
                        await message.answer(contact.read())
                    except:
                        pass
                    os.remove('contact.txt')
            else:
                await message.answer("Нету контактов")
        else:
            await message.answer("Вы не имеете право получать такую информацию")

executor.start_polling(dp)