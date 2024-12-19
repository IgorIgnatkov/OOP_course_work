import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from database.engine import drop_db, create_db, session_maker
from middlewares.db import DataBaseSession

from handlers.user_private_chat import user_private_router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv('TOKEN'))

dp = Dispatcher()

dp.include_router(user_private_router)


async def on_startup(bot):
    run_param = False
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    print('Бот лег')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
