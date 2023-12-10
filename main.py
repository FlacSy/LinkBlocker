# main.py
import os
import yaml
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка токена из .env файла
TOKEN = os.getenv("TELEGRAM_TOKEN")
if TOKEN is None:
    raise ValueError("Токен не найден. Пожалуйста, добавьте токен в файл .env")

# Загрузка списка запрещенных ссылок из файла links.yaml
with open("links.yaml", "r") as file:
    forbidden_links = yaml.safe_load(file)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)



async def is_admin(message: types.Message) -> bool:
    # Получаем информацию о чате
    chat_member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    # Проверяем, является ли пользователь администратором в текущем чате
    return chat_member.is_chat_admin()


async def delete_message(message: types.Message):
    try:
        # Проверка каждого сообщения на наличие запрещенных ссылок
        for link in forbidden_links:
            if link in message.text:
                # Проверка, является ли отправитель сообщения администратором
                if not await is_admin(message):
                    # Логирование информации о сообщении и ссылке
                    logger.info(
                        f"Сообщение от {message.from_user.username} ({message.from_user.id}) в чате {message.chat.title} содержит запрещенную ссылку: {message.text}"
                    )
                    await message.delete()
                    await bot.send_message(message.chat.id, f"@{message.from_user.username} отправил запрещенную ссылку")
                    break  # Если найдена хотя бы одна запрещенная ссылка, прерываем проверку
    except Exception as e:
        logger.error(f"Произошла ошибка при обработке сообщения: {e}")


@dp.message_handler()
async def echo_all(message: types.Message):
    await delete_message(message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
