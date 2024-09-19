from aiogram import Router,F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery,KeyboardButton,ReplyKeyboardMarkup,ContentType

from set_app.settings import BUT,DESCR,USERMOD,ADMIN_ID,CHANEL_ID

from ...utils.db.class_db import SQLiteCRUD
from ...states.state_user.state_us import StateUser
from ...filters.chat_type import chat_type_filter,MediaFilter
from ...keyboards.inline.button import CreateInline,CreateBut

user_private_router_uz = Router()
user_private_router_uz.message.filter(chat_type_filter(['private']))

db = SQLiteCRUD('db.sqlite3')

@user_private_router_uz.callback_query(F.data=='Izoh koldiring')
async def mes(call:CallbackQuery,state:FSMContext):
    await call.message.answer('Izoh')
    await state.set_state(StateUser.comment_uz)

@user_private_router_uz.message(StateUser.comment_uz,F.text)
async def mes1(message:Message,state:FSMContext):
    comment = message.text
    url = message.from_user.url
    name = message.from_user.full_name
    await message.bot.send_message(
        chat_id=CHANEL_ID,
        text=f'comment from user <a href="{url}"><b>{name}</b></a>\nComment: {comment}'
    )
    await message.answer('Izoh kildirganigiz uchun harmat')
    await state.clear()

# uz_start
@user_private_router_uz.callback_query(F.data=='uz')
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    for i in db.read(DESCR,where_clause='title_id = 4'):
        des = i[1]
    await call.message.answer(
        des,
        reply_markup=CreateBut([p[1] for p in db.read(BUT)],back_uz='Orqaga')
    )
    await state.set_state(StateUser.school_uz)

@user_private_router_uz.callback_query(F.data=='back_uz')
async def back(call:CallbackQuery,state:FSMContext):
    for i in db.read(DESCR,where_clause=f'title_id = {1}'):
            text = i[1]
    await call.message.answer(
        f'{text}',
        reply_markup=CreateInline(ru='Ru',uz='Uz')
    )
    await state.clear()

@user_private_router_uz.callback_query(F.data,StateUser.school_uz)
async def name(call:CallbackQuery,state:FSMContext):
    school = call.data
    await state.update_data({'school':school})
    for i in db.read(DESCR,where_clause='title_id = 3'):
        title = i[1]
    await call.message.answer(title)
    await state.set_state(StateUser.name_uz)

@user_private_router_uz.message(F.text,StateUser.name_uz)
async def name1(message:Message,state:FSMContext):
    title = message.text
    await state.update_data({'title':title})
    for i in db.read(DESCR,where_clause='title_id = 5'):
        city = i[1]
    await message.answer(city)
    await state.set_state(StateUser.city_uz)

@user_private_router_uz.message(F.text,StateUser.city_uz)
async def city1(message:Message,state:FSMContext):
    city = message.text
    await state.update_data({'city':city})
    for i in db.read(DESCR,where_clause='title_id = 6'):
        number = i[1]

    contact_button = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                text="Kontaktni yuboring",
                request_contact=True
                )
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(number,reply_markup=contact_button)
    await state.set_state(StateUser.number_uz)

@user_private_router_uz.message(F.contains,StateUser.number_uz)
async def num(message:Message,state:FSMContext):
    num = message.contact.phone_number
    await state.update_data({'num':num})
    for i in db.read(DESCR,where_clause='title_id = 7'):
        py = i[1]
    await message.answer(py,reply_markup=CreateInline('Onlyne tolov','Borib tolash'))
    await state.set_state(StateUser.py_uz)

@user_private_router_uz.callback_query(F.data=='Onlyne tolov',StateUser.py_uz)
async def py(call:CallbackQuery,state:FSMContext):
    await call.message.answer('Tolov Chekini yuboring')
    await state.set_state(StateUser.py1_uz)

@user_private_router_uz.message(StateUser.py1_uz,MediaFilter())
async def handle_media(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.content_type == ContentType.PHOTO:
        name = data.get('title')
        url = message.from_user.url
        photo_id = message.photo[-1].file_id
        for admin_id  in ADMIN_ID:
            await message.bot.send_photo(
                chat_id= admin_id ,  # ID администратора
                photo=photo_id,
                caption=f"Чек от пользователя <a href='{url}'>{name}</a>",
                reply_markup=CreateInline('Qabul qiling', 'Rad etish')
            )
        await message.answer("Chekingiz tekshirish uchun yuborildi!")
        await state.set_state(StateUser.check_uz)

    elif message.content_type == ContentType.DOCUMENT:
        if message.document.mime_type == 'application/pdf':
            name = data.get('title')
            url = message.from_user.url
            for admin_id in ADMIN_ID:
                await message.bot.send_document(
                    chat_id= admin_id ,
                    document=message.document.file_id,
                    caption=f"PDF файл от пользователя <a href='{url}'>{name}</a>",
                    reply_markup=CreateInline('Qabul qiling', 'Rad etish')
                )
            await message.answer("Chekingiz tekshirish uchun yuborildi!")
            await state.set_state(StateUser.check_uz)
        else:
            await message.answer("Iltimos, fotosurat yoki PDF faylini yuboring.")

@user_private_router_uz.callback_query(F.data=='Qabul qiling',StateUser.check_uz)
async def check(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    py = True
    user_id = call.from_user.id
    db.insert(
        USERMOD, 
        telegram_id=user_id, 
        full_name=title, 
        school=school, city=city,
        number=str(num), 
        payment=py, 
        language='ru' 
    )
    await call.message.answer('Chekingiz qabul qilindi!')
    await state.clear()

@user_private_router_uz.callback_query(F.data=='Rad etish',StateUser.check_uz)
async def check(call:CallbackQuery,state:FSMContext):
    await call.message.answer('Chek tasdiqlanmadi!!!\n Chekingizni qayta yuboring!')
    await state.set_state(StateUser.py1_uz)


@user_private_router_uz.callback_query(F.data=='Borib tolash',StateUser.py_uz)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    py = False
    user_id = call.from_user.id
    db.insert(
        USERMOD, 
        telegram_id=user_id, 
        full_name=title, 
        school=school, 
        city=city, 
        number=str(num), 
        payment=py, 
        language='uz' 
    )
    
    user_id = call.from_user.id
    main = db.read(
        USERMOD,
        where_clause=f'telegram_id = {user_id}'
    )
    if main:
        lg = main[0][7]
        if lg == 'ru':
            for i in db.read(DESCR,where_clause=f'title_id = {1}'):
                text = i[2]
            await call.message.answer(
                f'{text}',
                reply_markup=CreateInline('Оставить комментарий')
            )
        elif lg == 'uz':
            for i in db.read(DESCR,where_clause=f'title_id = {1}'):
                text = i[1]
            await call.message.answer(
                f'{text}',
                reply_markup=CreateInline('Izoh koldiring')
            )
        await state.clear()
# uz_end

