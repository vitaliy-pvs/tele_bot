from aiogram.utils import executor
from handlers.client import start_sending
from handlers.create_bot import dp
from data_base import sqlite_db
from handlers import client
import asyncio
import aioschedule


async def scheduler():
    aioschedule.every().day.at("10:00").do(start_sending)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(_):
    print('Бот запущен')
    sqlite_db.sql_start()
    asyncio.create_task(scheduler())

client.register_handlers_client(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
