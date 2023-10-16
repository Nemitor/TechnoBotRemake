import os
import re
import sys
import time

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, Application, \
    ContextTypes

import loggerTech
from database import get_all_requests, insert_in_db, get_active_status, change_status
from dictionary import address
from errors import EmptyBase, IdNotExists, ImportEmpty
from modules.utils import convert_time_to_gmt5, create_txt, formatting_request

SELECTING_ADDRESS, ENTER_ROOM, ENTER_MESSAGE, ENTER_NAME = range(4)

logger = loggerTech.logger

try:
    load_dotenv()
    TOKEN = os.getenv("TOKEN")
    sys_admins = os.getenv("SYS_ADMINS").split(',')
except AttributeError:
    logger.error(".env")
    sys.exit(0)

sys_admins = [int(admin_id) for admin_id in sys_admins]
bot = Bot(token=TOKEN)

address_keyboard = [[address[0], address[1], address[2]],
                    [address[3], address[4], address[5]]]

regex_pattern = '|'.join(re.escape(building) for building in address)
regex_pattern = f'^({regex_pattern})$'


async def start(update: Update, context: CallbackContext):
    context.user_data['telegram_id'] = update.message.from_user.id

    await update.message.reply_text(
        "Здравствуйте! Для отправки запроса в техническую службу выберите адрес:",
        reply_markup=ReplyKeyboardMarkup(
            address_keyboard, one_time_keyboard=True),
    )
    logger.info(f"User {update.message.from_user.id}, Create the new conversation!")

    return SELECTING_ADDRESS


# Функция для обработки выбора адреса
async def select_address(update, context):
    context.user_data['address'] = update.message.text
    await update.message.reply_text(
        f"Вы выбрали адрес: {context.user_data['address']}. Введите кабинет:", reply_markup=ReplyKeyboardRemove())

    return ENTER_ROOM


# Функция для обработки ввода номера кабинета
async def enter_room(update, context):
    context.user_data['room'] = update.message.text
    await update.message.reply_text("Введите сообщение:")

    return ENTER_MESSAGE


# Функция для обработки ввода сообщения
async def enter_message(update, context):
    context.user_data['message'] = update.message.text
    await update.message.reply_text("Введите ваше имя:")

    return ENTER_NAME


async def processing_user_request(update, context):
    await update.message.reply_text("Спасибо! Ваша информация принята.")

    context.user_data['name'] = update.message.text
    last_message = "От:  " + context.user_data['name'] + "\n" + \
                   "По адресу: " + context.user_data['address'] + "\n" + \
                   "В кабинете: " + context.user_data['room'] + "\n" + \
                   "Сообщение: " + context.user_data['message']

    await send_to_sys_admins(last_message)

    insert_in_db(context.user_data['name'], address.index(context.user_data['address']), context.user_data['room'],
                 context.user_data['message'], int(time.time()), update.message.from_user.id, True)
    logger.info(f"User {update.message.from_user.id}, Create the new request!")
    return ConversationHandler.END


async def cancel(update, context):
    await update.message.reply_text(
        "Диалог отменен.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


async def send_to_sys_admins(message: str):
    for admin_id in sys_admins:
        try:
            await bot.sendMessage(text=message, chat_id=admin_id)
        except BadRequest:
            logger.error("Cant send message to sys_admin id:" + str(admin_id))


async def send_log(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in sys_admins:
        await update.message.reply_text("Извините, вы не имеете доступа к этой функции")
        return
    try:
        txt_path = create_txt(formatting_request(get_all_requests()))
        await bot.sendDocument(caption="По моей информации, это актуальная база", chat_id=user_id,
                               document=open(txt_path, 'rb'))
        os.remove(txt_path)
        logger.info(f"Admin: {update.message.from_user.id}. Get logs")
    except (EmptyBase, ImportEmpty):
        await update.message.reply_text("На данный момент, база пустая", reply_markup=ReplyKeyboardRemove())
        logger.info(f"Admin: {update.message.from_user.id}. Cant take empty base")


async def admin_start_status(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in sys_admins:
        await update.message.reply_text("Извините, вы не имеете доступа к этой функции")
        return ConversationHandler.END
    address_keyboard.append(["Все адреса"])
    await update.message.reply_text(
        "По какому адресу хотите узнать активные запросы?",
        reply_markup=ReplyKeyboardMarkup(
            address_keyboard, one_time_keyboard=True),
    )
    del address_keyboard[2]
    return SELECTING_ADDRESS


async def send_active_status(update: Update, context: CallbackContext):
    build_id = update.message.text
    if build_id == "Все адреса":
        req = get_active_status(0)
    else:
        req = get_active_status(address.index(build_id))

    if not req:
        await update.message.reply_text(f"Активных заявок по адресу: {build_id}\nНе обнаружено.")
        return ConversationHandler.END
    await update.message.reply_text(f"Активные заявки по адресу: {build_id}")
    for row in req:
        formatted_datetime = convert_time_to_gmt5(row[5])

        result_str = '\n'.join([
            f'ID: {row[0]}\n'
            f'Имя учителя: {row[1]},\n'
            f'По адресу: {address[row[2]]}\n'
            f'Кабинет: {row[3]}\n'
            f'Время запроса: {formatted_datetime}\n'
            f'Message: {row[4]}'
        ])
        await update.message.reply_text(result_str)
    return ConversationHandler.END


async def send_active_status_apply(update: Update, context: CallbackContext):
    await send_active_status(update, context)
    await update.message.reply_text("Для изменения статуса напишите ID:")
    return ENTER_ROOM


async def apply_request(update: Update, context: CallbackContext):
    request_id = update.message.text
    try:
        status = change_status(int(request_id))
        user_tg_id = status[6]
        formatted_datetime = convert_time_to_gmt5(status[5])
        try:
            await bot.sendMessage(text=f"Ваша заявка от: {formatted_datetime} выполнена", chat_id=user_tg_id)
        except BadRequest:
            logger.error(f"Cant send massage to user {user_tg_id}")
        await update.message.reply_text(f"ID: {request_id}, отмечен как выполненный\n"
                                        f"Пользователь {user_tg_id}, получил сообщение о выполненной работе")
    except IdNotExists as e:
        await update.message.reply_text(f"ID: {request_id}. Не существует, и/или случилась непредвиденная ошибка")
        logger.warning(f"W{e} with request_id: {request_id} unreachable!")

    return ConversationHandler.END


user_chat_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SELECTING_ADDRESS: [
            MessageHandler(
                filters.Regex(regex_pattern), select_address)],
        ENTER_ROOM: [MessageHandler(filters.TEXT & (~ filters.COMMAND), enter_room)],
        ENTER_MESSAGE: [MessageHandler(filters.TEXT & (~ filters.COMMAND), enter_message)],
        ENTER_NAME: [MessageHandler(filters.TEXT & (~ filters.COMMAND), processing_user_request)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

admin_get_active_status = ConversationHandler(
    entry_points=[CommandHandler('status', admin_start_status)],
    states={SELECTING_ADDRESS: [
        MessageHandler(filters.Regex(f'{regex_pattern}|Все адреса'), send_active_status)],
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

admin_get_TXT = CommandHandler('log', send_log)

admin_apply_request = ConversationHandler(
    entry_points=[CommandHandler('apply', admin_start_status)],
    states={SELECTING_ADDRESS: [
        MessageHandler(filters.Regex(f'{regex_pattern}|Все адреса'), send_active_status_apply)],
        ENTER_ROOM: [MessageHandler(filters.TEXT & (~ filters.COMMAND), apply_request)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)


def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(user_chat_handler)
    application.add_handler(admin_get_TXT)
    application.add_handler(admin_get_active_status)
    application.add_handler(admin_apply_request)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
