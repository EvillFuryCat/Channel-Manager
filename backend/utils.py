from ChatGPT.GPT import GPTAnalytics
from db.db import RedisManager
from telethon import TelegramClient
import env


CLIENT_NAME = env.USERNAME
CHANNELS = env.CHANNELS
GPT_KEY = env.GPT_KEY
PROMPT_FOR_CATEGORY = "Select three key words from this text. The answer should always be in three words and in English"
PROMPT_FOR_REWRITE = "Перепиши этот текст, как будто ты крутой хакер, и добавь индивидуальности. Отвечай только на русском"
SYSTEM_MESSAGE_FOR_REWRITE = (
    "Ты очень полезный помощник который умело переписывает тексты"
)
SYSTEM_MESSAGE_FOR_CATEGORY = (
    "You are a helpful assistant who answers in just three words"
)
PUBSUB_CHANNEL = env.PUBSUB_CHANNEL


def text_preparation(post: str):
    lines = post.strip().split("\n")
    aligned_text = "".join(line.strip() for line in lines)
    return aligned_text


async def rewrite(text: str):
    chat_GPT = GPTAnalytics(GPT_KEY)
    with RedisManager(host="0.0.0.0", port=6379, db=0) as redis:
        rewrite_text = chat_GPT.chat_with_model(
            SYSTEM_MESSAGE_FOR_REWRITE, PROMPT_FOR_REWRITE, text
        )
        redis.publish(PUBSUB_CHANNEL, rewrite_text)


def check_similarity(db: RedisManager, target_string: str) -> bool:
    if db.get_data(target_string) is not None:
        return True
    else:
        target_words = target_string.split(", ")
        keys = db.get_keys()
        for target_key in target_words:
            for key in keys:
                key = key.decode("utf-8").split(", ")
                if target_key in key:
                    return True

    return False


async def id_check(id_post: int, post: str) -> bool:
    with RedisManager(host="0.0.0.0", port=6379, db=0) as redis:
        if redis.get_data(id_post) is None:
            redis.save_in_redis(id_post, post, 259200)
            return True
        else:
            return False


async def categorize(id_post: list, post: list):
    chat_GPT = GPTAnalytics(GPT_KEY)
    with RedisManager(host="0.0.0.0", port=6379, db=0) as redis:
        if await id_check(id_post, post):
            list_of_category = chat_GPT.chat_with_model(
                SYSTEM_MESSAGE_FOR_CATEGORY, PROMPT_FOR_CATEGORY, post
            )
            if check_similarity(redis, list_of_category) is True:
                return None
            redis.save_in_redis(list_of_category, post, 259200)
            return post
