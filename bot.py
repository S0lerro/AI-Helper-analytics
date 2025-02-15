import telebot
from telebot import types
import sqlite3



t = open('TOKEN.txt')
TOKEN = t.read().strip()
print(TOKEN)
t.close()
bot = telebot.TeleBot(TOKEN)
categories = ['категории типа 1', '2 категория ', '3 категори']
dates = ['эта неделя', 'прошлая неделя', 'последний месяц']


def generate_message(callback):
    new = callback.data
    print(new)
    if new == 'main_menu':
        menu = types.InlineKeyboardMarkup(row_width=2)
        menu.add(types.InlineKeyboardButton("Создать запрос", callback_data="create1"))
        menu.add(types.InlineKeyboardButton("Информация", callback_data="inf"))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text="Привет, я бот выбери что надо", reply_markup=menu)
    elif new == 'create1':
        markup_cat = types.InlineKeyboardMarkup(row_width=2)
        for cur in categories:
            markup_cat.add(types.InlineKeyboardButton(cur, callback_data="create2 " + str(cur)))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text="Выберите категорию:", reply_markup=markup_cat)
    elif new.startswith("create2"):
        date_cat = types.InlineKeyboardMarkup(row_width=2)
        cat = new.split()[1]
        date_cat.add(types.InlineKeyboardButton("Эта неделя", callback_data= 'create3 ' + ' ' + cat + " 1"))
        date_cat.add(types.InlineKeyboardButton("Прошлая неделя", callback_data='create3' + ' ' + cat + " 2"))
        date_cat.add(types.InlineKeyboardButton("Последний месяц", callback_data='create3 ' + ' ' + cat + " 3"))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text="Выберите период:", reply_markup=date_cat)
    elif new.startswith("create3"):
        cat = new.split()
        print(cat)
        menu_create = types.InlineKeyboardMarkup(row_width=2)
        menu_create.add(types.InlineKeyboardButton("Начать поиск", callback_data='create4 ' + cat[1] + ' ' + cat[2] + " 0"))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text="Вы выбрали дату и категорию: " + cat[1] + cat[2], reply_markup=menu_create)
    elif new.startswith("create4"):
        if new.split()[3] == '0':
            cat = new.split()
            main_db = sqlite3.connect('websites.db')
            cursor = main_db.cursor()
            menu_create = types.InlineKeyboardMarkup(row_width=2)
            menu_create.add(types.InlineKeyboardButton("Веррнуться в меню", callback_data='main_menu'))
            all_text = ''
            cursor.execute('SELECT site_name, description, time_author, link FROM websites')
            rows = cursor.fetchall()
            all_text = ''
            # Форматирование и вывод данных
            for row in rows:
                site_name, description, time_author, link = row
                all_text += f"{site_name}\n\n{description}\n\n{time_author}\n\n{link}\n------------------------\n"

            bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.id, text=all_text, reply_markup=menu_create)
            main_db.close()

@bot.message_handler(commands=["start"])
def start(message):
    menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    btn = types.KeyboardButton("Меню")
    menu_markup.add(btn)

    bot.send_message(message.chat.id, "Добро пожаловать бла бла бла", reply_markup=menu_markup)
    #add_to_db(message.chat.id)


@bot.message_handler(content_types=['text'])
def menu(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Категории', callback_data="create1")
    btn2 = types.InlineKeyboardButton(text='Информация', callback_data="inf")
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, text="Основное меню", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: True)
def inline_callback(callback):
    generate_message(callback)


if __name__ == '__main__':
    #create_table()
    bot.polling(none_stop=True)
