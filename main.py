from telethon.sync import TelegramClient
from db.config import Singleton
import env
import schedule
import time
import logging

API_ID = env.API_TOKEN
API_HASH = env.API_HASH
CLIENT_NAME = env.USERNAME
CHANNELS = env.CHANNELS

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)


def get_channel_messages(api_id, api_hash, channel_username):
    with TelegramClient(CLIENT_NAME, api_id, api_hash) as client:
        messages = client.get_messages(channel_username)
        return messages


def main():
    channel_username = CHANNELS
    for channel in channel_username:
        messages = get_channel_messages(API_ID, API_HASH, channel)
        for message in messages:
            with Singleton.get_connection() as db:
                db.set(channel, message.message, 259200)
                text = db.get(channel).decode("utf-8")
                print(channel)
                print(text)


# main()
schedule.every(5).minutes.do(main)

while True:
   schedule.run_pending()
   time.sleep(1)
