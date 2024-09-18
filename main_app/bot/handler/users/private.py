from aiogram import Router,F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message,CallbackQuery,KeyboardButton,ReplyKeyboardMarkup,ContentType

from set_app.settings import but,decs,usermod,ADMIN_ID,CHANEL_ID

from ...filters.chat_type import chat_type_filter,MediaFilter
from ...states.state_user.state_us import StateUser
from ...keyboards.inline.button import CreateInline,CreateBut
from ...utils.db.class_db import SQLiteCRUD

user_private_router = Router()
user_private_router.message.filter(chat_type_filter(['private']))

db = SQLiteCRUD('db.sqlite3')

@user_private_router.message(CommandStart())
async def private_start(message:Message):
    user_id = message.from_user.id
    main = db.read(
        usermod,
        where_clause=f'telegram_id = {user_id}'
    )
    if main:
        lg = main[0][7]
        if lg == 'ru':
            for i in db.read(decs,where_clause=f'title_id = {1}'):
                text = i[2]
            await message.answer(
                f'{text}',
                reply_markup=CreateInline('Оставить комментарий')
                )
        elif lg == 'uz':
            for i in db.read(decs,where_clause=f'title_id = {1}'):
                text = i[1]
            await message.answer(
                f'{text}',
                reply_markup=CreateInline('Izoh koldiring'  )
                )
    else:
        for i in db.read(decs,where_clause=f'title_id = {1}'):
            text = i[1]
        await message.answer(
            f'{text}',
            reply_markup=CreateInline(ru='Ru',uz='Uz')
            )

@user_private_router.callback_query(F.data=='Оставить комментарий')
async def mes(call:CallbackQuery,state:FSMContext):
    await call.message.answer('Ваш комментарий')
    await state.set_state(StateUser.comment)

@user_private_router.message(StateUser.comment,F.text)
async def mes1(message:Message,state:FSMContext):
    comment = message.text
    url = message.from_user.url
    name = message.from_user.full_name
    await message.bot.send_message(
        chat_id=CHANEL_ID,
        text=f'comment from user <a href="{url}"><b>{name}</b></a>:\n{comment}'
    )
    await message.answer('спасибо за коммент')
    await state.clear()

# ru_start
@user_private_router.callback_query(F.data=='ru')
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    for i in db.read(decs,where_clause='title_id = 4'):
        des = i[2]
    await call.message.answer(
        des,
        reply_markup=CreateBut([p[2] for p in db.read(but)],back_ru='Назад')
    )
    await state.set_state(StateUser.school)

@user_private_router.callback_query(F.data=='back_ru',StateUser.school)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    for i in db.read(decs,where_clause=f'title_id = {1}'):
            text = i[1]
    await call.message.answer(
        f'{text}',
        reply_markup=CreateInline(ru='Ru',uz='Uz')
        )
    await state.clear()

@user_private_router.callback_query(F.data,StateUser.school)
async def name(call:CallbackQuery,state:FSMContext):
    school = call.data
    await state.update_data({'school':school})
    for i in db.read(decs,where_clause='title_id = 3'):
        title = i[2]
    await call.message.answer(title)
    await state.set_state(StateUser.name)

@user_private_router.message(F.text,StateUser.name)
async def name1(message:Message,state:FSMContext):
    title = message.text
    await state.update_data({'title':title})
    for i in db.read(decs,where_clause='title_id = 5'):
        city = i[2]
    await message.answer(city)
    await state.set_state(StateUser.city)

@user_private_router.message(F.text,StateUser.city)
async def city1(message:Message,state:FSMContext):
    city = message.text
    await state.update_data({'city':city})
    for i in db.read(decs,where_clause='title_id = 6'):
        number = i[2]

    contact_button = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="Отправить контакт", 
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True
    )
    await message.answer(number,reply_markup=contact_button)
    await state.set_state(StateUser.number)

@user_private_router.message(F.contains,StateUser.number)
async def num(message:Message,state:FSMContext):
    num = message.contact.phone_number
    await state.update_data({'num':num})
    for i in db.read(decs,where_clause='title_id = 7'):
        py = i[2]
    await message.answer(
        py,
        reply_markup=CreateInline('Оплатить Онляйн','Прийти и заплатить')
    )
    await state.set_state(StateUser.py)

@user_private_router.callback_query(F.data=='Оплатить Онляйн',StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    await call.message.answer('Отправьте чек')
    await state.set_state(StateUser.py1)

@user_private_router.message(StateUser.py1,MediaFilter())
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
                reply_markup=CreateInline('Принять', 'Отклонить')
            )
        await message.answer("Ваш чек отправлено на проверку!")
        await state.set_state(StateUser.check)

    elif message.content_type == ContentType.DOCUMENT:
        if message.document.mime_type == 'application/pdf':
            name = data.get('title')
            url = message.from_user.url
            for admin_id in ADMIN_ID:
                await message.bot.send_document(
                    chat_id= admin_id ,
                    document=message.document.file_id,
                    caption=f"PDF файл от пользователя <a href='{url}'>{name}</a>",
                    reply_markup=CreateInline('Принять', 'Отклонить')
                )
            await message.answer("Ваш чек отправлено на проверку!")
            await state.set_state(StateUser.check)
    else:
        await message.answer("Пожалуйста, отправьте Фото или PDF файл.")

@user_private_router.callback_query(F.data=='Принять',StateUser.check)
async def check(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    py = True
    user_id = call.from_user.id
    db.insert(
        usermod, 
        telegram_id=user_id, 
        full_name=title, 
        school=school, 
        city=city, 
        number=str(num), 
        payment=py, 
        language='ru' 
    )
    await call.message.answer('Ваш чек принят!')
    await state.clear()

@user_private_router.callback_query(F.data=='Отклонить',StateUser.check)
async def check(call:CallbackQuery,state:FSMContext):
    await call.message.answer('Чек не прошел проверку!!!\n Отправьте ваш чек Заново!')
    await state.set_state(StateUser.py1)

@user_private_router.callback_query(F.data=='Прийти и заплатить',StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    data = await state.get_data()
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    py = False
    user_id = call.from_user.id
    db.insert(
        usermod, 
        telegram_id=user_id, 
        full_name=title, 
        school=school, 
        city=city, 
        number=str(num), 
        payment=py, 
        language='ru' 
    )
    
    user_id = call.from_user.id
    main = db.read(
        usermod,
        where_clause=f'telegram_id = {user_id}'
    )
    if main:
        lg = main[0][7]
        if lg == 'ru':
            for i in db.read(decs,where_clause=f'title_id = {1}'):
                text = i[2]
            await call.message.answer(
                f'{text}',
                reply_markup=CreateInline('Оставить комментарий')
            )
        elif lg == 'uz':
            for i in db.read(decs,where_clause=f'title_id = {1}'):
                text = i[1]
            await call.message.answer(
                f'{text}',
                reply_markup=CreateInline('Izoh koldiring')
            )
        await state.clear()
# ru_end
