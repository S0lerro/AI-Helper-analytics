import telebot
from apscheduler.schedulers.background import BackgroundScheduler
import sqlite3


def create_table():
    users_db = sqlite3.connect('users.db')
    c = users_db.cursor()
    try:
        c.execute("""CREATE TABLE users (
            tg_id text
        )""")
    except:
        pass
    c.execute("INSERT INTO users VALUES('1716995834')")
    users_db.commit()


t = open('TOKEN.txt')
TOKEN = t.read()
t.close()
bot = telebot.TeleBot(TOKEN)



def add_to_db(ID):
    db = sqlite3.connect('users.db')
    c = db.cursor()
    c.execute("INSERT INTO users (tg_id) VALUES (?)", (ID,))
    db.commit()
    db.close()



def daily_send_message():
    db = sqlite3.connect('users.db')
    c = db.cursor()
    c.execute("SELECT tg_id FROM users")
    users = c.fetchall()
    db.close()

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
    create_table()
    schedule_daily_poll()
    bot.polling(none_stop=True)
