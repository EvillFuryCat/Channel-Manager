import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import MessageEntity

from db.db import RedisManager


BOT_TOKEN: str = os.getenv("BOT_TOKEN")
HOST: str = os.getenv("HOST")
PORT: int = os.getenv("PORT")
DB: int = os.getenv("DB")
TELEGRAM_CHANNEL_ID: str = os.getenv("TELEGRAM_CHANNEL_ID")

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def send_message():
    with RedisManager(host=HOST, port=PORT, db=DB) as redis:
        pubsub = redis.pubsub()
        pubsub.subscribe("my_channel")
        for message in pubsub.listen():
            if (
                message["type"] != "subscribe"
                and message["channel"] == b"my_channel"
                and message["data"].decode("utf-8") != ""
            ):
                await bot.send_message(
                    chat_id=TELEGRAM_CHANNEL_ID,
                    text=message["data"],
                    # entities=,
                    # parse_mode=
                )


async def main():
    await send_message()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logger.info("Starting the application")
    asyncio.run(main())
