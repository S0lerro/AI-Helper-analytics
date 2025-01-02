import telebot
from telebot import types
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
categories = ['категории типа 1','2 категория ','3 категори']
dates = ['эта неделя','прошлая неделя','последний месяц']

def add_to_db(ID):
    db = sqlite3.connect('users.db')
    c = db.cursor()
    c.execute("INSERT INTO users (tg_id) VALUES (?)", (ID,))
    db.commit()
    db.close()

def users_ids_from_db():
    db = sqlite3.connect('users.db')
    c = db.cursor()
    c.execute("SELECT tg_id FROM users")
    users = c.fetchall()
    db.close()
    return users

def daily_send_message():
    users = users_ids_from_db()
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
    menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn = types.KeyboardButton("Меню")
    menu_markup.add(btn)
    
    bot.send_message(message.chat.id, "Добро пожаловать бла бла бла",reply_markup = menu_markup)
    add_to_db(message.chat.id)

@bot.message_handler(content_types = ['text'])
def menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text = 'Категории', callback_data="CAT")
    btn2 = types.InlineKeyboardButton(text = 'Информация', callback_data="NOTHING")
    markup.add(btn1,btn2)
    bot.send_message(message.from_user.id, text="Основное меню",reply_markup=markup)
    print(11111111)



@bot.callback_query_handler(func=lambda callback: True)
def inline_callback(callback):
        if callback.data == "CAT":
            call = callback
            markup_cat = types.InlineKeyboardMarkup(row_width=2)
            for cur in categories:
                markup_cat.add(types.InlineKeyboardButton(cur, callback_data="DAT"+str(cur)))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Выберите категорию:", reply_markup = markup_cat)
        elif callback.data.startswith("DAT"):
            call = callback
            date_cat = types.InlineKeyboardMarkup(row_width=2)
            date_cat.add(types.InlineKeyboardButton("Эта неделя", callback_data="1"+call.data))
            date_cat.add(types.InlineKeyboardButton("Прошлая неделя", callback_data="2"+call.data))
            date_cat.add(types.InlineKeyboardButton("Последний месяц", callback_data="3"+call.data))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text="Выберите период:", reply_markup = date_cat)
        else:
            d = dates[int(callback.data[0])-1]
            c = " "+callback.data[4::]
            menu = types.InlineKeyboardMarkup(row_width=2)
            menu.add(types.InlineKeyboardButton("Вернуться в меню", callback_data="menu"))
            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text="Вы выбрали дату и категорию: "+ d + c, reply_markup = menu)

if __name__ == '__main__':
    create_table()
    #schedule_daily_poll()
    bot.polling(none_stop=True)
