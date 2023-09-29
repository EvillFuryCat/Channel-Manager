import env
import logging
from telethon import TelegramClient, events

from backend.utils import (
    text_preparation,
    categorize,
    rewrite,
)


API_ID = env.API_TOKEN
API_HASH = env.API_HASH
CHANNELS = env.CHANNELS

logging.basicConfig(
    filename="log.json",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING,
)

logger = logging.getLogger(__name__)

client = TelegramClient("session_name", API_ID, API_HASH)


@client.on(events.NewMessage(chats=(CHANNELS)))
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
