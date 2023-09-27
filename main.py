from telethon.sync import TelegramClient
from db.db import RedisManager
from ChatGPT.GPT import GPTAnalytics, GPT_KEY
import env
import schedule
import time
import logging

from utils.utils import check_similarity

API_ID = env.API_TOKEN
API_HASH = env.API_HASH
CLIENT_NAME = env.USERNAME
CHANNELS = env.CHANNELS
PROMPT = "Select three key words from this text. The answer should always be in three words and in English"

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)


def get_list_channel_messages(api_id: str, api_hash: str):
    channel_username = CHANNELS
    list_of_posts = []
    for channel in channel_username:
        with TelegramClient(CLIENT_NAME, api_id, api_hash) as client:
            messages = client.get_messages(channel)
            for message in messages:
                list_of_posts.append(message.message)
    return list_of_posts


def text_preparation():
    posts = get_list_channel_messages(API_ID, API_HASH)
    ready_text = []
    for post in posts:
        lines = post.strip().split("\n")
        aligned_text = "".join(line.strip() for line in lines)
        ready_text.append(aligned_text)
    return ready_text


def categorize() -> None:
    categorize_GPT = GPTAnalytics(GPT_KEY)
    posts = text_preparation()
    with RedisManager() as redis:
        for post in posts:
            list_of_category = categorize_GPT.chat_with_model(PROMPT, post)
            if check_similarity(redis, list_of_category) is True:
                break
            redis.save_in_redis(list_of_category, post, 259200)


def main():
    pass


categorize()
# schedule.every(5).minutes.do(main)

# while True:
#    schedule.run_pending()
#    time.sleep(1)
