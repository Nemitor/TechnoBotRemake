import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

from Sheets import set_new_sheet_data
from config import TOKEN, sys_admins

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

SELECTING_ADDRESS, ENTER_ROOM, ENTER_MESSAGE, ENTER_NAME = range(4)

bot = Bot(token=TOKEN)


# Начальная функция диалога
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


# Функция для обработки ввода имени и завершения диалога
def enter_name(update, context):
    context.user_data['name'] = update.message.text
    set_new_sheet_data(context.user_data)
    # Здесь вы можете использовать context.user_data для доступа ко всем данным пользователя, собранным в ходе диалога
    last_message = "От:  " + context.user_data['name'] + "\n" + \
                   "По адресу: " + context.user_data['address'] + "\n" + \
                   "В кабинете: " + context.user_data['room'] + "\n" + \
                   "Сообщение: " + context.user_data['message']

    send_to_sys_admins(last_message)

    update.message.reply_text("Спасибо! Ваша информация принята.")

    return ConversationHandler.END


# Функция для отмены диалога
def cancel(update, context):
    update.message.reply_text(
        "Диалог отменен.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def send_to_sys_admins(message):
    for admin_id in sys_admins:
        try:
            bot.sendMessage(text=message, chat_id=admin_id)
        except:
            print("Cant send message to sys_admin id:" + str(admin_id))


def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Создаем обработчики стадий диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ADDRESS: [
                MessageHandler(Filters.regex('^(Мелик-Карамова 4/1|Рабочая 43|Крылова.д 41/1|50 ЛетВЛКСМ|Кукуевицкого '
                                             '2|Дзержинского 6/1)$'), select_address)],
            ENTER_ROOM: [MessageHandler(Filters.text & (~ Filters.command), enter_room)],
            ENTER_MESSAGE: [MessageHandler(Filters.text & (~ Filters.command), enter_message)],
            ENTER_NAME: [MessageHandler(Filters.text & (~ Filters.command), enter_name)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dispatcher.add_handler(conv_handler)

    # Запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
