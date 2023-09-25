import logging
import os

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters

SELECTING_ADDRESS, ENTER_ROOM, ENTER_MESSAGE, ENTER_NAME = range(4)

load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
sys_admins = os.getenv("sys_admins").split(',')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.user_data['telegram_id'] = update.message.from_user.id
    reply_keyboard = [["Мелик-Карамова 4/1", "Рабочая 43", "Крылова.д 41/1"],
                      ["50 ЛетВЛКСМ", "Кукуевицкого 2", "Дзержинского 6/1"]]
    update.message.reply_text(
        "Привет, выберите адрес:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True),
    )

    return SELECTING_ADDRESS


# Функция для обработки выбора адреса
def select_address(update, context):
    context.user_data['address'] = update.message.text
    update.message.reply_text(
        f"Вы выбрали адрес: {context.user_data['address']}. Введите кабинет:", reply_markup=ReplyKeyboardRemove())

    return ENTER_ROOM


# Функция для обработки ввода номера кабинета
def enter_room(update, context):
    context.user_data['room'] = update.message.text
    update.message.reply_text("Введите сообщение:")

    return ENTER_MESSAGE


# Функция для обработки ввода сообщения
def enter_message(update, context):
    context.user_data['message'] = update.message.text
    update.message.reply_text("Введите ваше имя:")

    return ENTER_NAME


def processing_user_request(update, context):
    update.message.reply_text("Спасибо! Ваша информация принята.")

    context.user_data['name'] = update.message.text
    last_message = "От:  " + context.user_data['name'] + "\n" + \
                   "По адресу: " + context.user_data['address'] + "\n" + \
                   "В кабинете: " + context.user_data['room'] + "\n" + \
                   "Сообщение: " + context.user_data['message']

    send_to_sys_admins(bot, last_message, sys_admins)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(
        "Диалог отменен.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def send_to_sys_admins(bot: Bot, message: str, sys_admins):
    for admin_id in sys_admins:
        try:
            bot.sendMessage(text=message, chat_id=admin_id)
        except:
            print("Cant send message to sys_admin id:" + str(admin_id))


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    user_chat_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ADDRESS: [
                MessageHandler(Filters.regex('^(Мелик-Карамова 4/1|Рабочая 43|Крылова.д 41/1|50 ЛетВЛКСМ|Кукуевицкого '
                                             '2|Дзержинского 6/1)$'), select_address)],
            ENTER_ROOM: [MessageHandler(Filters.text & (~ Filters.command), enter_room)],
            ENTER_MESSAGE: [MessageHandler(Filters.text & (~ Filters.command), enter_message)],
            ENTER_NAME: [MessageHandler(Filters.text & (~ Filters.command), processing_user_request)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    # Создаем обработчики стадий диалога
    dispatcher.add_handler(user_chat_handler)

    # Запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
