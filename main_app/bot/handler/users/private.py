from aiogram import Router,F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandStart
from aiogram.types import Message,CallbackQuery,KeyboardButton,ReplyKeyboardMarkup,ContentType,FSInputFile,InlineKeyboardButton,ReplyKeyboardRemove
from set_app.settings import BUT,DESCR,USERMOD,ADMIN_ID,CHANEL_ID,SAVE_DATA

from ...utils.db.class_db import SQLiteCRUD
from ...states.state_user.state_us import StateUser
from ...filters.chat_type import chat_type_filter,MediaFilter,create_excel_with_data
from ...keyboards.inline.button import CreateInline,CreateBut

user_private_router = Router()
user_private_router.message.filter(chat_type_filter(['private']))

db = SQLiteCRUD('db.sqlite3')

@user_private_router.message(CommandStart())
async def private_start(message:Message,state:FSMContext):
    user_id = message.from_user.id
    await state.update_data({'user_id':user_id})
    user_check = db.read(SAVE_DATA,where_clause=f'telegram_id = {user_id}')
    if user_check == None:
        main = db.read(
            USERMOD,
            where_clause=f'telegram_id = {user_id}'
        )
        if main:
            lg = main[0][7]
            if lg == 'ru':
                for i in db.read(DESCR,where_clause=f'title_id = {1}'):
                    text = i[2]
                await message.answer(
                    f'{text}'
                )
            elif lg == 'uz':
                for i in db.read(DESCR,where_clause=f'title_id = {1}'):
                    text = i[1]
                await message.answer(
                    f'{text}'
                )
        else:
            for i in db.read(DESCR,where_clause=f'title_id = {1}'):
                text = i[1]
            await message.answer(
                f'{text}',
                reply_markup=CreateInline(ru='Ru',uz='Uz')
            )
    else:
        await message.answer('Ваша заявка уже отправлена')

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
    for i in db.read(DESCR,where_clause='title_id = 4'):
        des = i[2]
    await call.message.answer(
        des,
        reply_markup=CreateBut([p[2] for p in db.read(BUT)],back_ru='Назад')
    )
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state(StateUser.school)

@user_private_router.callback_query(F.data=='back_ru',StateUser.school)
async def cmd_ru(call:CallbackQuery,state:FSMContext):
    for i in db.read(DESCR,where_clause=f'title_id = {1}'):
            text = i[1]
    await call.message.answer(
        f'{text}',
        reply_markup=CreateInline(ru='Ru',uz='Uz')
    )
    call.message.edit_reply_markup(reply_markup=None)
    await state.clear()

@user_private_router.callback_query(F.data,StateUser.school)
async def name(call:CallbackQuery,state:FSMContext):
    school = call.data
    await state.update_data({'school':school})
    for i in db.read(DESCR,where_clause='title_id = 3'):
        title = i[2]
    await call.message.answer(title)
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state(StateUser.name)

@user_private_router.message(F.text,StateUser.name)
async def name1(message:Message,state:FSMContext):
    title = message.text
    await state.update_data({'title':title})
    for i in db.read(DESCR,where_clause='title_id = 5'):
        city = i[2]
    await message.answer(city)
    await state.set_state(StateUser.city)

@user_private_router.message(F.text,StateUser.city)
async def city1(message:Message,state:FSMContext):
    city = message.text
    await state.update_data({'city':city})
    for i in db.read(DESCR,where_clause='title_id = 6'):
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
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(number,reply_markup=contact_button)
    await state.set_state(StateUser.number)

@user_private_router.message(F.contains,StateUser.number)
async def num(message:Message,state:FSMContext):
    num = message.contact.phone_number

    if num.startswith('+380') and len(num) == 13:
        await state.update_data({'num':num})
        for i in db.read(DESCR,where_clause='title_id = 7'):
            py = i[2]
        await message.answer(
            py,
            reply_markup=CreateInline('Оплатить Онляйн','Прийти и заплатить')
        )
        await state.set_state(StateUser.py)
    else:
        # Если номер не из Узбекистана
        await message.answer(
            "Пожалуйста, отправьте узбекский номер, который начинается с +998."
        )


@user_private_router.callback_query(F.data=='Оплатить Онляйн',StateUser.py)
async def py(call:CallbackQuery,state:FSMContext):
    await call.message.answer('Отправьте чек',reply_markup=ReplyKeyboardRemove())
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state(StateUser.py1)

@user_private_router.message(StateUser.py1,MediaFilter())
async def handle_media(message: Message, state: FSMContext):
    data = await state.get_data()

    user_id = data.get('user_id')
    num = data.get('num')
    city = data.get('city')
    title = data.get('title')
    school = data.get('school')
    
    button = InlineKeyboardBuilder()
    button.add(InlineKeyboardButton(text='Принять',callback_data=f'Tr_{user_id}'))
    button.add(InlineKeyboardButton(text='Отклонить',callback_data=f'Fr_{user_id}'))
    button.adjust(2)

    if message.content_type == ContentType.PHOTO:

        url = message.from_user.url
        photo_id = message.photo[-1].file_id

        db.insert(
            SAVE_DATA,
            telegram_id = user_id,
            full_name = title,
            school = school,
            city = city,
            number = num,
            language = 'ru'
        )

        await message.bot.send_photo(
            chat_id= CHANEL_ID ,  # ID администратора
            photo=photo_id,
            caption=f"Чек от пользователя <a href='{url}'><b>{title}</b></a>",
            reply_markup=button.as_markup()
        )
        await message.answer("Ваш чек отправлено на проверку!")

    elif message.content_type == ContentType.DOCUMENT:
        if message.document.mime_type == 'application/pdf':
            url = message.from_user.url

            db.insert(
                SAVE_DATA,
                telegram_id = user_id,
                full_name = title,
                school = school,
                city = city,
                number = num,
                language = 'ru'
            )

            await message.bot.send_document(
                chat_id= CHANEL_ID ,
                document=message.document.file_id,
                caption=f"PDF файл от пользователя <a href='{url}'><b>{title}</b></a>",
                reply_markup=button.as_markup()
            )
            await message.answer("Ваш чек отправлено на проверку!",reply_markup=CreateInline('Оставить комментарий'))
    else:
        await message.answer("Пожалуйста, отправьте Фото или PDF файл.")

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
        USERMOD, 
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
            await call.message.edit_reply_markup(reply_markup=None)

        elif lg == 'uz':
            for i in db.read(DESCR,where_clause=f'title_id = {1}'):
                text = i[1]
            await call.message.answer(
                f'{text}',
                reply_markup=CreateInline('Izoh koldiring')
            )
            await call.message.edit_reply_markup(reply_markup=None)
        await state.clear()
# ru_end
