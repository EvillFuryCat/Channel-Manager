from db.db import RedisManager

import json
import os
import tiktoken


TIME_LIFE: int = os.getenv("TIME_LIFE")
DEBUG = os.getenv("DEBUG")

encoding = tiktoken.get_encoding("cl100k_base")


def deserialize(message):
    data = json.loads(message)
    message_id = data["message_id"]
    post = data["message"]
    return message_id, post


def text_preparation(post: str, max_tokens: int = 4096):
    count_token = len(encoding.encode(post))
    if count_token >= max_tokens:
        while len(count_token) > 500:
            count_token.pop()
        allowed_text_length = encoding.decode(count_token)
        return allowed_text_length
    return post


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


async def id_check(redis: RedisManager, id_post: int, post: str) -> bool:
    if redis.get_data(id_post) is None:
        redis.save_in_redis(id_post, post, TIME_LIFE)
        return True
    else:
        return False
