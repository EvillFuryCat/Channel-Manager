import logging
import os
from telethon import TelegramClient, events

from utils import (
    text_preparation,
    categorize,
    rewrite,
)


TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_CHANNELS: list = os.getenv("TELEGRAM_CHANNELS").split(",")
SESSION_NAME = os.getenv("SESSION_NAME")

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)


client = TelegramClient(SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)


@client.on(events.NewMessage(TELEGRAM_CHANNELS))
async def normal_handler(event):
    message = event.message.to_dict()["message"]
    post_id = event.message.to_dict()["id"]
    ready_text = text_preparation(message)
    define_category = await categorize(post_id, ready_text)
    if define_category:
        await rewrite(define_category)


if __name__ == "__main__":
    logger.info("Starting the application")
    client.start()
    client.run_until_disconnected()
