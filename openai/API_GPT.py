import os
import openai


openai.api_key = "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"

completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "user", "content": "Tell the world about the ChatGPT API in the style of a pirate."}
  ]
)

print(completion.choices[0].message.content)