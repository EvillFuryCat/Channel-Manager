import asyncio
import logging
import os
import tiktoken
import openai
from colorama import Fore, Back, init

from db.db import RedisManager
from utils import (
    text_preparation,
    id_check,
    deserialize,
    check_similarity,
)

GPT_KEY: str = os.getenv("GPT_KEY")
PROMPT_FOR_CATEGORY: str = os.getenv("PROMPT_FOR_CATEGORY")
PROMPT_FOR_REWRITE: str = os.getenv("PROMPT_FOR_REWRITE")
SYSTEM_MESSAGE_FOR_REWRITE: str = os.getenv("SYSTEM_MESSAGE_FOR_REWRITE")
SYSTEM_MESSAGE_FOR_CATEGORY: str = os.getenv("SYSTEM_MESSAGE_FOR_CATEGORY")
HOST: str = os.getenv("HOST")
PORT: int = os.getenv("PORT")
DB: int = os.getenv("DB")
DEBUG = os.getenv("DEBUG")
TIME_LIFE: int = os.getenv("TIME_LIFE")


logging.basicConfig(
    filename="gpt_log.json",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.WARNING,
)

logger = logging.getLogger(__name__)


class GPTAnalytics:
    def __init__(
        self,
        api_key: str,
        redis_host: str,
        redis_port: int,
        redis_db: int,
    ) -> None:
        self.api_key = api_key
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        openai.api_key = api_key
        

    async def listen_channel(self):
        encoding = tiktoken.get_encoding("cl100k_base")
        with RedisManager(
            host=self.redis_host, port=self.redis_port, db=self.redis_db
        ) as redis:
            pubsub = redis.pubsub()
            pubsub.subscribe("post_for_in_gpt_channel")
            for message in pubsub.listen():
                try:
                    if (
                        message["type"] == "message"
                        and message["data"].decode("utf-8") != ""
                    ):
                        data = message["data"].decode("utf-8")
                        post_id, post = deserialize(data)
                        ready_text = text_preparation(post, encoding)
                        response: str = await self.chat_with_model(
                            SYSTEM_MESSAGE_FOR_CATEGORY,
                            PROMPT_FOR_CATEGORY,
                            ready_text,
                        )
                        if await check_similarity(redis, response.lower()) is True:
                            if DEBUG == "True":
                                init(autoreset=True)
                                print(
                                    Fore.CYAN
                                    + "### Такие тезисы уже существуют! Не сохраняю!"
                                )
                                print(response)
                            continue
                        if DEBUG == "True":
                            init(autoreset=True)
                            print(
                                Back.CYAN + "### Тезисы, которые выделил ChatGPT:"
                            )
                            print(response)
                        redis.save_in_redis(response.lower(), ready_text, TIME_LIFE)
                        rewrite = await self.chat_with_model(
                            SYSTEM_MESSAGE_FOR_REWRITE,
                            PROMPT_FOR_REWRITE,
                            ready_text,
                        )
                        redis.publish("my_channel", rewrite)
                except Exception as e:
                    logger.error(f"Произошла ошибка: {str(e)}")

    async def chat_with_model(
        self, system_message: str, prompt: str, user_message: str
    ):
        while True:
        
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{prompt}\n{user_message}"},
            ]

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
            chat_response = completion.choices[0].message.content
            messages.append({"role": "assistant", "content": chat_response})

            return chat_response


if __name__ == "__main__":
    logger.info("Starting the application")
    analytics = GPTAnalytics(GPT_KEY, redis_host=HOST, redis_port=PORT, redis_db=DB)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(analytics.listen_channel())
