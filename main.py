import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from environs import Env

# import model
from handlers import router

# import env config file

env = Env()
env.read_env()  #'../.env', recurse=False)


async def main():
    bot = Bot(token=env("BOT_TOKEN"), parse_mode=ParseMode.HTML)
    # emb_model = model.init_model()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, encoding="utf-8")
    asyncio.run(main())
