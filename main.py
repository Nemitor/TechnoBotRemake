import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters

from sql_data import get_txt_requests

SELECTING_ADDRESS, ENTER_ROOM, ENTER_MESSAGE, ENTER_NAME = range(4)

load_dotenv()
try:
    TOKEN = os.getenv("TOKEN")
    sys_admins = os.getenv("sys_admins").split(',')
except:
    print(".env is not detected in root folder")
    sys.exit(0)
sys_admins = [int(admin_id) for admin_id in sys_admins]
bot = Bot(token=TOKEN)

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

    send_to_sys_admins(bot, last_message)
    return ConversationHandler.END


def cancel(update, context):
    update.message.reply_text(
        "Диалог отменен.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def send_to_sys_admins(bot: Bot, message: str):
    for admin_id in sys_admins:
        try:
            bot.sendMessage(text=message, chat_id=admin_id)
        except:
            print("Cant send message to sys_admin id:" + str(admin_id))


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


def send_log(update, context):
    user_id = update.message.from_user.id
    if user_id not in sys_admins:
        update.message.reply_text("Извините, вы не имеете доступа к этой функции")
        return
    txt_path = get_txt_requests()
    bot.sendDocument(caption="По моей информации, это актуальная база", chat_id=user_id,  document=open(txt_path, 'rb'))
    os.remove(txt_path)


admin_get_TXT = CommandHandler('log', send_log)

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(user_chat_handler)
    dispatcher.add_handler(admin_get_TXT)

    # Запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
