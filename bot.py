import telebot
from apscheduler.schedulers.background import BackgroundScheduler


t = open('TOKEN.txt')

TOKEN = t.read()
t.close()
print(TOKEN)
bot = telebot.TeleBot(TOKEN)
users = ['']

def add_to_db(ID):
    pass


def daily_send_message():
    for chat_id in users:
        bot.send_message(chat_id, 'текст')

def schedule_daily_poll():
    scheduler = BackgroundScheduler()

    scheduler.add_job(daily_send_message(), 'cron', hour=7, minute=0)
    scheduler.add_job(daily_send_message(), 'cron', hour=13, minute=0)
    scheduler.add_job(daily_send_message(), 'cron', hour=19, minute=0)

    scheduler.start()

@bot.message_handler(commands="start")
def start(message):
    bot.send_message(message.chat_id, "Добро пожаловать бла бла бла")
    add_to_db(message.chat_id)

if __name__ == '__main__':
    schedule_daily_poll()
    bot.polling(none_stop=True)
