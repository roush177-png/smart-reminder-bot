import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime

# Твой токен
TOKEN = '8029769418:AAEutxiaLcBzlKj3vnduWcEJAAaoSjZFjZU'

# Словарь для напоминаний (user_id: list of {'text': str, 'time': 'HH:MM'})
reminders = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Команда /start от user_id={update.effective_user.id}")
    await update.message.reply_text('Привет! Я Smart Reminder Pro. Напиши /remind <текст> <HH:MM> для напоминания.')

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Команда /remind от user_id={update.effective_user.id}, args={context.args}")
    if not context.args or len(context.args) < 2:
        await update.message.reply_text('Формат: /remind <текст> <HH:MM> (например, /remind Тест 15:50)')
        return
    text = ' '.join(context.args[:-1])
    time_str = context.args[-1]
    try:
        datetime.strptime(time_str, '%H:%M')
    except ValueError:
        await update.message.reply_text('Ошибка: Время должно быть в формате HH:MM (например, 15:50).')
        return
    user_id = update.effective_user.id
    if user_id not in reminders:
        reminders[user_id] = []
    reminders[user_id].append({'text': text, 'time': time_str})
    await update.message.reply_text(f'Напоминание "{text}" на {time_str} добавлено!')
    logger.info(f"Добавлено: user_id={user_id}, текст={text}, время={time_str}")

async def check_reminders(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime('%H:%M')
    logger.info(f"Проверка времени: {now}, напоминания: {reminders}")
    for user_id, rems in list(reminders.items()):
        for rem in list(rems):
            if rem['time'] == now:
                try:
                    await context.bot.send_message(chat_id=user_id, text=f'Напоминание: {rem["text"]}')
                    logger.info(f"Отправлено: user_id={user_id}, текст={rem['text']}")
                    rems.remove(rem)
                except Exception as e:
                    logger.error(f"Ошибка отправки: {e}")

def main():
    try:
        application = Application.builder().token(TOKEN).build()
        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler('remind', remind))
        # Запускаем повторяющуюся задачу каждую минуту для проверки напоминаний
        application.job_queue.run_repeating(check_reminders, interval=60, first=0)
        logger.info("Бот запущен, polling начат, check_reminders запланирован каждую минуту")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")
        raise

if __name__ == '__main__':
    main()