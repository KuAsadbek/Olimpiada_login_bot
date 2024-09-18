from aiogram.types import ReplyKeyboardMarkup,KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def CreateReply(*args) -> ReplyKeyboardBuilder:
    bulder = ReplyKeyboardBuilder()
    for i in args:
        bulder.add(KeyboardButton(text=i))
    bulder.adjust(2)

