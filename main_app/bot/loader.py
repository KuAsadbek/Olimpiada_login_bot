import asyncio
from aiogram import Bot,Dispatcher
from aiogram.client.bot import DefaultBotProperties

from handler.users.private import user_private_router
from handler.users.private_uz import user_private_router_uz
from handler.group.groups import group_router

from utils.db.class_db import SQLiteCRUD,decs

db = SQLiteCRUD('db.sqlite3')

BOT_TOKEN = db.read(decs,where_clause=f'title_id = {8}')

bot = Bot(token=BOT_TOKEN[0][1],default=DefaultBotProperties(parse_mode='HTML'))
ds = Dispatcher()

ds.include_routers(user_private_router,user_private_router_uz,group_router)

async def on_startup(bot):
    print('I work')

async def main():
    ds.startup.register(on_startup)
    await ds.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())