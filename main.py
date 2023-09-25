import os
import logging
from telegram import Bot
from telegram.ext import Updater
from dotenv import load_dotenv
from telegram_bot import user_chat_handler

SELECTING_ADDRESS, ENTER_ROOM, ENTER_MESSAGE, ENTER_NAME = range(4)

load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Создаем обработчики стадий диалога
    dispatcher.add_handler(user_chat_handler)

    # Запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
