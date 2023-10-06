from db.db import RedisManager
import os
import tiktoken


HOST: str = os.getenv("HOST")
PORT: int = os.getenv("PORT")
DB: int = os.getenv("DB")
TIME_LIFE: int = os.getenv("TIME_LIFE")
DEBUG = os.getenv("DEBUG")


def text_preparation(post: str, max_tokens: int = 4096):
    encoding = tiktoken.get_encoding("cl100k_base")
    count_token = len(encoding.encode(post))
    if count_token >= max_tokens:
        while len(count_token) > 500:
            count_token.pop()
        allowed_text_length = encoding.decode(count_token)
        return allowed_text_length
    return post


async def rewrite(text: str):
    with RedisManager(host=HOST, port=PORT, db=DB) as redis:
        redis.publish("post_for_rewriting_in_gpt_channel", text)


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
    with RedisManager(host=HOST, port=PORT, db=DB) as redis:
        if redis.get_data(id_post) is None:
            redis.save_in_redis(id_post, post, TIME_LIFE)
            return True
        else:
            return False


async def categorize(id_post, post):
    with RedisManager(host=HOST, port=PORT, db=DB) as redis:
        if await id_check(id_post, post):
            redis.publish("post_to_category_channel_for_gpt", post)
            pubsub = redis.pubsub()
            pubsub.subscribe("get_from_category_channel_gpt")
            for message in pubsub.listen():
                if (
                    message["type"] == "message"
                    and message["data"].decode("utf-8") != ""
                ):
                    response = message["data"].decode("utf-8")
                    if check_similarity(redis, response) is True:
                        if DEBUG == "True":
                            print(
                                f"### Такие тезисы уже существуют! Не сохраняю!\n{response}"
                            )
                            break
                        break
                    redis.save_in_redis(response, post, 259200)
                    if DEBUG == "True":
                        print(f"### Тезисы, которые выделил ChatGPT:\n{response}")
                    return post
