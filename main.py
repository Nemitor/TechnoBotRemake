import logging
import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import Updater, CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters

from dictionary import address
from sql_data import get_txt_requests, insert_in_db, get_active_status

SELECTING_ADDRESS, ENTER_ROOM, ENTER_MESSAGE, ENTER_NAME = range(4)

try:
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    sys_admins = os.getenv("SYS_ADMINS").split(',')
except:
    print(".env is not detected in root folder")
    sys.exit(0)

sys_admins = [int(admin_id) for admin_id in sys_admins]
bot = Bot(token=TOKEN)
address_keyboard = [["Мелик-Карамова 4/1", "Рабочая 43", "Крылова.д 41/1"],
                    ["50 ЛетВЛКСМ", "Кукуевицкого 2", "Дзержинского 6/1"]]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


def start(update: Update, context: CallbackContext):
    context.user_data['telegram_id'] = update.message.from_user.id

    update.message.reply_text(
        "Привет, выберите адрес:",
        reply_markup=ReplyKeyboardMarkup(
            address_keyboard, one_time_keyboard=True),
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


def found_key(dictionary, search_key) -> int:
    founded_key = None
    for key, value in dictionary.items():
        if value == search_key:
            founded_key = key
            break
    return founded_key


def processing_user_request(update, context):
    update.message.reply_text("Спасибо! Ваша информация принята.")

    context.user_data['name'] = update.message.text
    last_message = "От:  " + context.user_data['name'] + "\n" + \
                   "По адресу: " + context.user_data['address'] + "\n" + \
                   "В кабинете: " + context.user_data['room'] + "\n" + \
                   "Сообщение: " + context.user_data['message']

    send_to_sys_admins(bot, last_message)

    insert_in_db(context.user_data['name'], found_key(address, context.user_data['address']), context.user_data['room'],
                 context.user_data['message'], int(time.time()), update.message.from_user.id, True)
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


def send_log(update, context):
    user_id = update.message.from_user.id
    if user_id not in sys_admins:
        update.message.reply_text("Извините, вы не имеете доступа к этой функции")
        return
    txt_path = get_txt_requests()
    bot.sendDocument(caption="По моей информации, это актуальная база", chat_id=user_id, document=open(txt_path, 'rb'))
    os.remove(txt_path)


def admin_start_status(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in sys_admins:
        update.message.reply_text("Извините, вы не имеете доступа к этой функции")
        return ConversationHandler.END
    reply_keyboard = [["Мелик-Карамова 4/1", "Рабочая 43", "Крылова.д 41/1"],
                      ["50 ЛетВЛКСМ", "Кукуевицкого 2", "Дзержинского 6/1"]]
    update.message.reply_text(
        "По какому адресу хотите узнать активные запросы?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True),
    )
    return SELECTING_ADDRESS


def send_active_status(update: Update, context: CallbackContext):
    build_id = update.message.text
    req = get_active_status(found_key(address,build_id))
    for row in req:
        current_datetime = datetime.fromtimestamp(row[5])
        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
        update.message.reply_text(f"Активные заявки по адресу: {build_id}")
        result_str = '\n'.join([
            f'ID: {row[0]}\n'
            f'Имя учителя: {row[1]},\n'
            f'По адресу: {address[row[2]]}\n'
            f'Кабинет: {row[3]}\n'
            f'Время запроса: {formatted_datetime}\n'
            f'Message: {row[4]}'
        ])
        update.message.reply_text(result_str)
    return ConversationHandler.END


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

admin_get_active_status = ConversationHandler(
    entry_points=[CommandHandler('status', admin_start_status)],
    states={SELECTING_ADDRESS: [
        MessageHandler(Filters.regex('^(Мелик-Карамова 4/1|Рабочая 43|Крылова.д 41/1|50 ЛетВЛКСМ|Кукуевицкого '
                                     '2|Дзержинского 6/1)$'), send_active_status)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

admin_get_TXT = CommandHandler('log', send_log)


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(user_chat_handler)
    dispatcher.add_handler(admin_get_TXT)
    dispatcher.add_handler(admin_get_active_status)

    # Запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
