from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
from deep_translator import GoogleTranslator
import logging

# Установим базовый уровень логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Глобальная переменная для хранения выбранного языка перевода
user_target_language = {}

# Функция для команды /start
async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [KeyboardButton("На английский"), KeyboardButton("На немецкий")],
        [KeyboardButton("На русский"), KeyboardButton("На французский")]
    ]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "Привет! Я бот-переводчик. Выберите язык, на который хотите перевести:",
        reply_markup=markup
    )

# Установка языка перевода
async def set_target_language(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text

    # Определяем язык перевода
    if "На английский" in user_text:
        target_lang = 'en'
    elif "На немецкий" in user_text:
        target_lang = 'de'
    elif "На русский" in user_text:
        target_lang = 'ru'
    elif "На французский" in user_text:
        target_lang = 'fr'
    else:
        await update.message.reply_text("Неизвестный язык. Попробуйте снова.")
        return

    # Сохраняем выбранный язык для текущего пользователя
    user_id = update.message.from_user.id
    user_target_language[user_id] = target_lang

    await update.message.reply_text(
        f"Язык перевода установлен: {user_text}. Теперь отправьте текст, который хотите перевести."
    )

# Перевод текста
async def translate_text(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Проверяем, выбран ли язык перевода
    if user_id not in user_target_language:
        await update.message.reply_text("Сначала выберите язык перевода с помощью кнопок.")
        return

    target_lang = user_target_language[user_id]
    user_text = update.message.text

    # Проверяем, не нажата ли кнопка действия
    if user_text in ["Перевести ещё текст", "Сменить язык перевода", "Завершить"]:
        return

    try:
        # Автоматическое определение языка текста
        translated_text = GoogleTranslator(source='auto', target=target_lang).translate(user_text)
        await update.message.reply_text(f"Перевод: {translated_text}")

        # Добавляем кнопки для выбора дальнейших действий
        keyboard = [
            [KeyboardButton("Перевести ещё текст"), KeyboardButton("Сменить язык перевода")],
            [KeyboardButton("Завершить")]
        ]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "Что вы хотите сделать дальше?",
            reply_markup=markup
        )
    except Exception as e:
        await update.message.reply_text(f"Ошибка при переводе: {e}")

# Обработка кнопок "Перевести ещё текст", "Сменить язык перевода", "Завершить"
async def handle_post_translation_action(update: Update, context: CallbackContext) -> None:
    user_text = update.message.text

    if "Перевести ещё текст" in user_text:
        await update.message.reply_text("Введите текст, который хотите перевести.")
    elif "Сменить язык перевода" in user_text:
        await update.message.reply_text("Выберите новый язык перевода:")
        await start(update, context)  # Вызываем функцию для повторного выбора языка
    elif "Завершить" in user_text:
        await update.message.reply_text("Спасибо, что воспользовались ботом! До свидания!")
    else:
        await update.message.reply_text("Неизвестное действие. Попробуйте снова.")

# Основная функция для запуска бота
def main() -> None:
    # Введите сюда свой токен
    application = Application.builder().token("7662937017:AAHn3AO9X1V7Y4pbkozp9m8c-7MAVvV-Hn4").build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))  # Команда /start
    application.add_handler(MessageHandler(filters.Regex("На .*"), set_target_language))  # Выбор языка перевода
    application.add_handler(MessageHandler(filters.Regex("(Перевести ещё текст|Сменить язык перевода|Завершить)"), handle_post_translation_action))  # Кнопки действий
    application.add_handler(MessageHandler(filters.TEXT & ~filters.Regex("На .*") & ~filters.Regex("(Перевести ещё текст|Сменить язык перевода|Завершить)"), translate_text))  # Текст для перевода

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
