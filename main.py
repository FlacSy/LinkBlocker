import os
import re
import yaml
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

# Константы
ADMIN_CHAT_IDS = [-1002021667574, 136817688]

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка токена из файла .env
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("Токен не найден. Пожалуйста, добавьте токен в файл .env.")


# Ссылки, которые не подлежат удалению
allowed_links = ["https://t.me/sepi0lscommunity/", "https://t.me/nikitasepi0l"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

async def is_admin(message: types.Message) -> bool:
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return chat_member.is_chat_admin()

async def delete_message(message: types.Message):
    try:
        if message.from_user.id in ADMIN_CHAT_IDS:
            return

        # Найти все ссылки в тексте сообщения
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.text)

        # Проверить каждую ссылку на соответствие запрещенным
        for link in links:
            if "tiktok" in link or not any(link.startswith(allowed) for allowed in allowed_links):
                if not await is_admin(message):
                    logger.info(
                        f"Сообщение от {message.from_user.username} ({message.from_user.id}) в чате {message.chat.title} содержит запрещенную ссылку: {link}"
                    )
                    await message.delete()
                    await bot.send_message(
                        message.chat.id,
                        f"Сообщение от {message.from_user.username} ({message.from_user.id}) в чате {message.chat.title} содержит запрещенную ссылку: {link}"
                    )
                    break

    except Exception as e:
        logger.error(f"Произошла ошибка при обработке сообщения: {e}")

@dp.message_handler()
async def echo_all(message: types.Message):
    await delete_message(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
