import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import MessageEntity

from db.db import RedisManager


logging.basicConfig(
    filename="log.json",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING,
)

logger = logging.getLogger(__name__)

BOT_TOKEN = "6318131538:AAFVgE9nHLvQMMYMJWWRKcOzJ3PaPcPEIcw"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def send_message():
    with RedisManager(host="0.0.0.0", port=6379, db=0) as redis:
        pubsub = redis.pubsub()
        pubsub.subscribe("my_channel")
        for message in pubsub.listen():
            if (
                message["type"] != "subscribe"
                and message["channel"] == b"my_channel"
                and message["data"].decode("utf-8") != ""
            ):
                await bot.send_message(
                    chat_id="-1001908502023",
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
