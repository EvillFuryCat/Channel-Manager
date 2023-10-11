import logging
import os
from colorama import Back, init
from telethon import TelegramClient, events
import json

from db.db import RedisManager


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
    filename="client_log.json",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING,
)

client = TelegramClient(SESSION_NAME, TELEGRAM_API_ID, TELEGRAM_API_HASH)


@client.on(events.NewMessage(TELEGRAM_CHANNELS))
async def normal_handler(event):
    with RedisManager(host=HOST, port=PORT, db=DB) as redis:
        try:
            message = event.message.to_dict()["message"]
            message_id = event.message.to_dict()["id"]
            if DEBUG == "True":
                init(autoreset=True)
                print(Back.GREEN + "### Новый пост в телеграм канале:" + Back.RESET)
                print(message)
            data = {"message": message, "message_id": message_id}
            json_data = json.dumps(data)
            redis.publish("post_for_in_gpt_channel", json_data)
        except Exception as e:
            logger.error(f"### An error occurred: {str(e)}")


if __name__ == "__main__":
    logger.info("Starting the application")
    client.start()
    client.run_until_disconnected()
