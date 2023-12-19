import os
import re
import yaml
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

# Constants
ADMIN_CHAT_ID = -1002021667574

# Configuration logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load token from .env file
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Token not found. Please add the token to the .env file.")

# Load forbidden links from links.yaml file
with open("links.yaml", "r") as file:
    forbidden_links = yaml.safe_load(file)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def is_admin(message: types.Message) -> bool:
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.is_chat_admin()

async def delete_message(message: types.Message):
    try:
        if message.from_user.id == ADMIN_CHAT_ID:
            return

        forbidden_links_set = set(forbidden_links)
        for link in forbidden_links_set:
            if re.search(re.escape(link), message.text):
                if not await is_admin(message):
                    logger.info(
                        f"Сообщение от @{message.from_user.username} в чате {message.chat.title} содержит запрещенную ссылку: {message.text}"
                    )
                    await message.delete()
                    await bot.send_message(
                        message.chat.id,
                         f"Сообщение от @{message.from_user.username} в чате {message.chat.title} содержит запрещенную ссылку: {message.text}"
                    )
                    break

        if {"https://t.me/sepi0lscommunity/", "https://t.me/nikitasepi0l"} in message.text:
            return
    except Exception as e:
        logger.error(f"An error occurred while processing the message: {e}")

@dp.message_handler()
async def echo_all(message: types.Message):
    await delete_message(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
