# Здесь второй варинат модуля utils, используется сохранение при помощи id сообщения, будет полезно, если каналы не дублируют сообщения друг друга

from ChatGPT.GPT import GPTAnalytics
from db.db import RedisManager
from telethon import TelegramClient
import env


CLIENT_NAME = env.USERNAME
CHANNELS = env.CHANNELS
GPT_KEY = env.GPT_KEY
PROMPT = "Select three key words from this text. The answer should always be in three words and in English"
PUBSUB_CHANNEL = env.PUBSUB_CHANNEL


async def get_list_channel_messages(api_id: str, api_hash: str):
    channel_username = CHANNELS
    list_of_posts = []
    id_posts = []
    async with TelegramClient(CLIENT_NAME, api_id, api_hash) as client:
        for channel in channel_username:
            messages = await client.get_messages(channel)
            for message in messages:
                list_of_posts.append(message.message)
                id_posts.append(message.id)
    return id_posts, list_of_posts


def text_preparation(posts):
    # posts = get_list_channel_messages(API_ID, API_HASH)
    ready_text = []
    for post in posts:
        lines = post.strip().split("\n")
        aligned_text = "".join(line.strip() for line in lines)
        ready_text.append(aligned_text)
    return ready_text


async def double_check(id_list, posts) -> None:
    with RedisManager(host="0.0.0.0", port=6379, db=0) as redis:
        for i in range(len(id_list)):
            id_post = id_list[i]
            post = posts[i]
            if redis.get_data(id_post) is None:
                redis.save_in_redis(id_post, post, 259200)
                redis.publish(PUBSUB_CHANNEL, post)


def rewrite():
    pass


# def check_similarity(db, target_string: str) -> bool:
#     if db.get_data(target_string) is not None:
#         return True
#     else:
#         target_words = target_string.split(", ")
#         keys = db.get_keys()
#         for target_key in target_words:
#             for key in keys:
#                 key = key.decode("utf-8").split(", ")
#                 if target_key in key:
#                     return True

#     return False
