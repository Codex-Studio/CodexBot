from aiogram import Bot, Dispatcher, executor, types 
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import config
import psycopg2
import logging
import os
import time

bot = Bot(token = config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
connect = psycopg2.connect(
    user = config.DATABASE_USER,
    password = config.DATABASE_USER_PASSWORD,
    database = config.DATABASE_NAME,
    host = config.DATABASE_HOST,
)
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)

class MailingState(StatesGroup):
    mail = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"Здраствуйте, {message.from_user.full_name}. Чем могу помочь?")
    cur = connect.cursor()
    # cur.execute(f"CREATE TABLE IF NOT EXISTS telegram_users_telegramuser(user_id BIGINT, chat_id BIGINT);")
    cur.execute(f"SELECT * FROM telegram_users_telegramuser WHERE user_id = {message.from_user.id};")
    res = cur.fetchall()
    print(res)
    if res == []:
        cur.execute(f"INSERT INTO telegram_users_telegramuser (user_id, chat_id, first_name, last_name, username, added) VALUES ('{message.from_user.id}', '{message.chat.id}', '{message.from_user.first_name}', '{message.from_user.last_name}', '{message.from_user.username}', '{time.ctime()}');")
    connect.commit()

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
                            contact.write(f"{res.replace('False', '')}\n")
                        else:
                            await message.answer("Нет текущих контактов")
                            break
                with open('contact.txt', 'r') as contact:
                    try:
                        await message.answer(contact.read())
                    except:
                        pass
                    os.remove('contact.txt')
            else:
                await message.answer("Нету контактов")
        # else:
        #     await message.answer("Вы не имеете право получать такую информацию")

@dp.message_handler(commands=['create_admin'])
async def create_admin(message: types.Message):
    await message.answer("Суперадмин")

@dp.message_handler(commands=['mailing'])
async def mailing(message: types.Message):
    admin = connect.cursor()
    admin.execute(f"SELECT id_telegram FROM users_user;")
    result = admin.fetchall()
    for user in result:
        if message.from_user.id in user:
            await message.answer("Введите сообщение рассылки")
            await MailingState.mail.set()
            break
    else:
        await message.answer("У вас нету прав")

@dp.message_handler(state = MailingState.mail)
async def send_mailing(message: types.Message, state : FSMContext):
    admin = connect.cursor()
    admin.execute(f"SELECT id_telegram FROM users_user;")
    result = admin.fetchall()
    for user in result:
        if message.from_user.id in user:
            cur = connect.cursor()
            cur.execute("SELECT chat_id FROM telegram_users_telegramuser;")
            result = cur.fetchall()
            print(result)
            for i in result:
                await bot.send_message(chat_id=int(i[0]), text = message.text)
            await state.finish()
    await state.finish()

@dp.message_handler()
async def not_found(message: types.Message):
    await message.reply("Я вас не понял")

executor.start_polling(dp)