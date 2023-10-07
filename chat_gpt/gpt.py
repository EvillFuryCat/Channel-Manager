import asyncio
import logging
import os
import openai
from colorama import Back, Fore, init

from db.db import RedisManager

GPT_KEY: str = os.getenv("GPT_KEY")
PROMPT_FOR_CATEGORY: str = os.getenv("PROMPT_FOR_CATEGORY")
PROMPT_FOR_REWRITE: str = os.getenv("PROMPT_FOR_REWRITE")
SYSTEM_MESSAGE_FOR_REWRITE: str = os.getenv("SYSTEM_MESSAGE_FOR_REWRITE")
SYSTEM_MESSAGE_FOR_CATEGORY: str = os.getenv("SYSTEM_MESSAGE_FOR_CATEGORY")
HOST: str = os.getenv("HOST")
PORT: int = os.getenv("PORT")
DB: int = os.getenv("DB")
DEBUG = os.getenv("DEBUG")


logging.basicConfig(
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

    async def listen_сhannel(self):
        with RedisManager(
            host=self.redis_host, port=self.redis_port, db=self.redis_db
        ) as redis:
            pubsub = redis.pubsub()
            pubsub.subscribe(
                "post_to_category_channel_for_gpt", "post_for_rewriting_in_gpt_channel"
            )

            for message in pubsub.listen():
                try:
                    if (
                        message["type"] == "message"
                        and message["data"].decode("utf-8") != ""
                    ):
                        channel = message["channel"].decode("utf-8")
                        data = message["data"].decode("utf-8")
                        if channel == "post_to_category_channel_for_gpt":
                            user_message = data
                            response = await self.chat_with_model(
                                SYSTEM_MESSAGE_FOR_CATEGORY,
                                PROMPT_FOR_CATEGORY,
                                user_message,
                            )
                            if response:
                                redis.publish("get_from_category_channel_gpt", response)
                        elif channel == "post_for_rewriting_in_gpt_channel":
                            if DEBUG == "True":
                                init(autoreset=True)
                                print(
                                    Fore.GREEN + Back.GREEN + "### Такой текст получает ChatGPT для рерайта:"
                                )
                                print(data)
                            user_message = data
                            response = await self.chat_with_model(
                                SYSTEM_MESSAGE_FOR_REWRITE,
                                PROMPT_FOR_REWRITE,
                                user_message,
                            )
                            if response:
                                if DEBUG == "True":
                                    init(autoreset=True)
                                    print(Back.GREEN + "### Это рерайт ChatGPT:")
                                    print(response)
                                redis.publish("my_channel", response)
                except Exception as e:
                    print("Произошла ошибка:", e)

    async def chat_with_model(
        self, system_message: str, prompt: str, user_message: str
    ):
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"{prompt}\n{user_message}"},
        ]

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
        chat_response = completion.choices[0].message.content
        messages.append([{"role": "assistant", "content": chat_response}])

        return chat_response


if __name__ == "__main__":
    if DEBUG == "True":
        init(autoreset=True)
    logger.info("Starting the application")
    analytics = GPTAnalytics(GPT_KEY, redis_host=HOST, redis_port=PORT, redis_db=DB)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(analytics.listen_сhannel())
