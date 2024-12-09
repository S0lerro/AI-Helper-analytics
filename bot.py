import telebot
from apscheduler.schedulers.background import BackgroundScheduler


t = open('TOKEN.txt')

TOKEN = t.read()
t.close()
print(TOKEN)
bot = telebot.TeleBot(TOKEN)
users = [1716995834]

def add_to_db(ID):
    users.append(ID)
    print(users)
    pass


def daily_send_message():
    for chat_id in users:
        bot.send_message(chat_id, 'текст')

def schedule_daily_poll():
    scheduler = BackgroundScheduler()

    scheduler.add_job(daily_send_message, 'cron', hour=7, minute=0)
    scheduler.add_job(daily_send_message, 'cron', hour=13, minute=0)
    scheduler.add_job(daily_send_message, 'cron', hour=18, minute=0)

    scheduler.start()

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать бла бла бла")
    add_to_db(message.chat.id)

if __name__ == '__main__':
    schedule_daily_poll()
    bot.polling(none_stop=True)
