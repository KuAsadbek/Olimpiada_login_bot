from aiogram import Bot,Dispatcher
from set_app.settings import BOT_TOKEN
from aiogram.client.bot import DefaultBotProperties

from .handler.users.private import user_private_router
from .handler.users.private_uz import user_private_router_uz
from .handler.group.groups import group_router


bot = Bot(token=BOT_TOKEN,default=DefaultBotProperties(parse_mode='HTML'))
ds = Dispatcher()

ds.include_router(user_private_router)
ds.include_router(user_private_router_uz)   
ds.include_router(group_router)

async def on_startup(bot):
    print('I work')

async def main():
    ds.startup.register(on_startup)
    await ds.start_polling(bot)
