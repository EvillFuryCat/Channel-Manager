from db.db import RedisManager
import os


HOST: str = os.getenv("HOST")
PORT: int = os.getenv("PORT")
DB: int = os.getenv("DB")
TIME_LIFE: int = os.getenv("TIME_LIFE")


def text_preparation(post: str):
    lines = post.strip().split("\n")
    aligned_text = "".join(line.strip() for line in lines)
    return aligned_text


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
                        pass
                    redis.save_in_redis(response, post, 259200)
                    return post
