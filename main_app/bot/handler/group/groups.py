import os
from aiogram import Router,F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery,FSInputFile

from set_app.settings import DESCR,USERMOD,SAVE_DATA,BUT

from ...utils.db.class_db import SQLiteCRUD
from ...filters.chat_type import chat_type_filter,create_excel_with_data
from ...states.state_user.state_us import StateUser
from ...keyboards.inline.button import CreateInline,CreateBut

group_router = Router()
group_router.message.filter(chat_type_filter(['supergroup']))

db = SQLiteCRUD('db.sqlite3')

@group_router.message(CommandStart())
async def one_cmd(message:Message):
    await message.answer(f'Hi bro you need excel file?',CreateInline('send_excel'))

@group_router.callback_query(F.data=='send_excel')
async def send(call:CallbackQuery):
    all_users_data = db.read(USERMOD)
    true_users_data = db.read(USERMOD,where_clause='payment = 1')
    false_users_data = db.read(USERMOD,where_clause='payment = 0')
    # Создание файла Excel
    file_path = create_excel_with_data(all_users_data, true_users_data, false_users_data, "user_data.xlsx")

    # Проверка на существование файла
    if file_path and os.path.exists(file_path):
        # Отправка файла
        document = FSInputFile(file_path)
        await call.message.answer_document(document=document, caption='user_data.xlsx')
        await call.message.delete_reply_markup(reply_markup=None)
    else:
        await call.message.reply("Произошла ошибка при создании файла.")

@group_router.callback_query(F.data)
async def check(call:CallbackQuery,state:FSMContext):
    str_text, index = call.data.split('_')
    user_id = int(index)
    print(str_text,user_id,type(user_id))
    save_data = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id}')
    lg = save_data[0][7]

    if str_text == 'Tr':
        
        user = save_data[0][1]
        title = save_data[0][2]
        school = save_data[0][3]
        city = save_data[0][4]
        num = save_data[0][5]
        py = True

        db.insert(
            USERMOD,
            telegram_id = user,
            full_name = title,
            school = school,
            city = city,
            number = num,
            payment = py,
            language = lg
        )

        db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')

        if lg == 'ru':
            ru = 2
            r = 'Чек прошел проверку!!!'
        else:
            ru = 1
            r = 'Chek tasdiqlandi!!!'
        
        for i in db.read(DESCR,where_clause=f'title_id = {1}'):
            text = f'{i[ru]}\n\n{r}'

        await call.message.bot.send_message(
            chat_id=user_id,
            text=text
        )
        await call.message.edit_reply_markup(reply_markup=None)  

    elif str_text == 'Fr':
        if lg == 'ru':
            r = 2
            ru = 'Чек не прошел проверку!!!\n Пройдите регистрацию заново -> /start'
        else:
            r = 1
            ru = 'Tekshiruv tasdiqlanmadi!!!\nQayta ro\'yxatdan o\'ting -> /start'
        
        for i in db.read(DESCR,where_clause='title_id = 4'):
            des = f'{i[r]}\n\n{ru}'

        db.delete(SAVE_DATA,where_clause=f'telegram_id = {user_id}')

        await call.message.bot.send_message(
            chat_id=user_id,
            text=des,
            reply_markup=CreateBut([p[2] for p in db.read(BUT)],back_ru='Назад')
        )
        await state.set_state(StateUser.school)
        await call.message.edit_reply_markup(reply_markup=None)