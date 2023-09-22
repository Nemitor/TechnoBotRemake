import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from  config import TOKEN, sys_admins

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Определение стадий диалога
SELECTING_ADDRESS, ENTER_ROOM, ENTER_MESSAGE, ENTER_NAME = range(4)


# Начальная функция диалога
def start(update, context):
    reply_keyboard = [['Адрес 1', 'Адрес 2', 'Адрес 3'],
                      ['Адрес 4', 'Адрес 5', 'Адрес 6']]
    update.message.reply_text(
        "Привет, выберите адрес:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )

    return SELECTING_ADDRESS


# Функция для обработки выбора адреса
def select_address(update, context):
    user = update.message.from_user
    context.user_data['address'] = update.message.text
    update.message.reply_text(f"Вы выбрали адрес: {context.user_data['address']}. Введите кабинет:")

    return ENTER_ROOM


# Функция для обработки ввода номера кабинета
def enter_room(update, context):
    user = update.message.from_user
    context.user_data['room'] = update.message.text
    update.message.reply_text("Введите сообщение:")

    return ENTER_MESSAGE


# Функция для обработки ввода сообщения
def enter_message(update, context):
    user = update.message.from_user
    context.user_data['message'] = update.message.text
    update.message.reply_text("Введите ваше имя:")

    return ENTER_NAME


# Функция для обработки ввода имени и завершения диалога
def enter_name(update, context):
    user = update.message.from_user
    context.user_data['name'] = update.message.text
    # Здесь вы можете использовать context.user_data для доступа ко всем данным пользователя, собранным в ходе диалога
    print(context.user_data['address'], context.user_data['room'], context.user_data['message'], context.user_data['name'])

    # Завершаем диалог
    update.message.reply_text("Спасибо! Ваша информация принята.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


# Функция для отмены диалога
def cancel(update, context):
    user = update.message.from_user
    update.message.reply_text("Диалог отменен.", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def main():
    # Замените 'YOUR_BOT_TOKEN' на токен вашего бота
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Создаем обработчики стадий диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SELECTING_ADDRESS: [
                MessageHandler(Filters.regex('^(Адрес 1|Адрес 2|Адрес 3|Адрес 4|Адрес 5|Адрес 6)$'), select_address)],
            ENTER_ROOM: [MessageHandler(Filters.text, enter_room)],
            ENTER_MESSAGE: [MessageHandler(Filters.text, enter_message)],
            ENTER_NAME: [MessageHandler(Filters.text, enter_name)],
        },
        fallbacks=[MessageHandler(Filters.regex('^Отмена$'), cancel)]
    )

    dispatcher.add_handler(conv_handler)

    # Запускаем бота
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()