import logging
import os
from colorama import Back, init
from telethon import TelegramClient, events

from db.db import RedisManager
from utils import (
    text_preparation,
    categorize,
    rewrite,
)


HOST: str = os.getenv("HOST")
PORT: int = os.getenv("PORT")
DB: int = os.getenv("DB")
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_CHANNELS: list = os.getenv("TELEGRAM_CHANNELS").split(",")
SESSION_NAME = os.getenv("SESSION_NAME")
DEBUG = os.getenv("DEBUG")


logger = logging.getLogger(__name__)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING,
)


client = TelegramClient(SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)


@client.on(events.NewMessage(TELEGRAM_CHANNELS))
async def normal_handler(event):
    with RedisManager(host=HOST, port=PORT, db=DB) as redis:
        try:
            message = event.message.to_dict()["message"]
            post_id = event.message.to_dict()["id"]
            if DEBUG == "True":
                init(autoreset=True)
                print(Back.CYAN + "### Новый пост в телеграм канале:")
                print(message)
            ready_text = text_preparation(message)
            define_category = await categorize(redis, post_id, ready_text)
            if define_category:
                await rewrite(redis, define_category)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting the application")
    client.start()
    client.run_until_disconnected()
