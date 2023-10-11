from db.db import RedisManager

import json
import os


TIME_LIFE: int = os.getenv("TIME_LIFE")
DEBUG = os.getenv("DEBUG")


def deserialize(message):
    data = json.loads(message)
    message_id = data["message_id"]
    post = data["message"]
    return message_id, post


def text_preparation(post: str, token_counter, max_tokens: int = 4096):
    count_token = len(token_counter.encode(post))
    if count_token >= max_tokens:
        while len(count_token) > max:
            count_token.pop()
        allowed_text_length = encoding.decode(count_token)
        return allowed_text_length
    return post


async def check_similarity(redis: RedisManager, target_string: str) -> bool:
    if redis.exists(target_string) > 0:
        return True
    else:
        return False


async def id_check(redis: RedisManager, id_post: int, post: str) -> bool:
    if redis.get_data(id_post) is None:
        redis.save_in_redis(id_post, post, TIME_LIFE)
        return True
    else:
        return False
