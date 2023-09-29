import os
from typing import Any
from db.db import RedisManager
import openai

# GPT = env.GPT_KEY
# GPT_KEY = "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"


class GPTAnalytics:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        openai.api_key = api_key

    # def listen_сhannel(self):

    def chat_with_model(
        self, system_message: str, prompt: str, user_message: str
    ) -> Any:
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


# while True:
#     user_msg = str(input())
#     messages = [
#         {"role": "system", "content": system_msg},
#         {"role": "user", "content": user_msg}
#     ]

#     completion = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=messages
#     )
#     chat_response = completion.choices[0].message.content
#     print(chat_response)
#     messages.append([{"role": "assistant", "content": chat_response}])

# if __name__ == "__main__":
#     assistant = GPTAnalytics(API_KEY)

#     while True:
#         user_msg = input()
#         response = assistant.chat_with_model(user_msg)
#         print(response)
