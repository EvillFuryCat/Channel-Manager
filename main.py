import env
import logging
import asyncio


from utils.utils import get_list_channel_messages, text_preparation, categorize


API_ID = env.API_TOKEN
API_HASH = env.API_HASH

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.WARNING
)


async def main():
    posts = await get_list_channel_messages(API_ID, API_HASH)
    ready_text = text_preparation(posts)
    define_category = await categorize(ready_text)

asyncio.run(main())
# schedule.every(5).minutes.do(main)

# while True:
#    schedule.run_pending()
#    time.sleep(1)
