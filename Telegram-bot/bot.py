import telebot
from telebot import types
import sqlite3
import logging
import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

user_articles = {}
categories = {
    "Safety": [
        "Emergencies (Environmental)",
        "Physical Impacts",
        "Community health and Safety",
        "Employee Health and Safety",
        "Product Safety and Quality"
    ],
    "Environmental": [
        "Waste Management",
        "Climate Risks",
        "Greenhouse Gas Emissions",
        "Air Pollution",
        "Energy Efficiency and Renewable",
        "Hazardous Materials Management",
        "Soil and Groundwater Impact",
        "Wastewater Management",
        "Water Consumption",
        "Surface Water Pollution",
        "Natural Resources",
        "Landscape Transformation",
        "Land Rehabilitation",
        "Biodiversity",
        "Animal Welfare",
        "Environmental Management"
    ],
    "Sustainable Cities": [
        "Planning Limitations",
        "Land Acquisition and Resettlement (Environmental)"
    ],
    "Manufacturing": [
        "Supply Chain (Environmental)"
    ],
    "Culture": [
        "Cultural Heritage"
    ]
}
dates = ['Эта неделя', 'Прошлая неделя', 'За весь месяц']
sources = [['rbc.ru', 'ferra.ru', 'pro.rbc.ru', 'ekb.plus.rbc.ru', 'realty.rbc.ru','editorial.rbc.ru', 'wine.rbc.ru', 'rbcrealty.ru'],['Nature.com', 'https://www.artificialintelligence-news.com'],['RBC.ru', 'Ferra.ru','Nature.com', 'https://www.artificialintelligence-news.com']]
translation_dict = {
    "Safety": "Безопасность",
    "Environmental": "Экология",
    "Sustainable Cities": "Устойчивые города",
    "Manufacturing": "Производство",
    "Culture": "Культура",

    "Emergencies (Environmental)": "Чрезвычайные ситуации (экологические)",
    "Physical Impacts": "Физические воздействия",
    "Community health and Safety": "Здоровье и безопасность сообществ",
    "Employee Health and Safety": "Здоровье и безопасность сотрудников",
    "Product Safety and Quality": "Безопасность и качество продукции",

    "Waste Management": "Управление отходами",
    "Climate Risks": "Климатические риски",
    "Greenhouse Gas Emissions": "Выбросы парниковых газов",
    "Air Pollution": "Загрязнение воздуха",
    "Energy Efficiency and Renewable": "Энергоэффективность и возобновляемые источники энергии",
    "Hazardous Materials Management": "Управление опасными материалами",
    "Soil and Groundwater Impact": "Воздействие на почву и подземные воды",
    "Wastewater Management": "Управление сточными водами",
    "Water Consumption": "Потребление воды",
    "Surface Water Pollution": "Загрязнение поверхностных вод",
    "Natural Resources": "Природные ресурсы",
    "Landscape Transformation": "Преобразование ландшафта",
    "Land Rehabilitation": "Восстановление земель",
    "Biodiversity": "Биоразнообразие",
    "Animal Welfare": "Благополучие животных",
    "Environmental Management": "Управление окружающей средой",
    "Supply Chain (Environmental)": "Цепочка поставок (экологическая)",

    "Planning Limitations": "Ограничения планирования",
    "Land Acquisition and Resettlement (Environmental)": "Приобретение земель и переселение (экологические)",

    "Cultural Heritage": "Культурное наследие"
}

t = open('../TOKEN.txt')
TOKEN = t.read().strip()
t.close()
bot = telebot.TeleBot(TOKEN)



def period(n):
    l = []
    wd = int(datetime.datetime.now().weekday())
    d = datetime.datetime.now().date()
    if n == 1:
        for i in range(wd+1):
            l.append(d-datetime.timedelta(days = i))
        for i in range(6-wd):
            l.append(str(d+datetime.timedelta(days = i)))
    return l

def get_articles_from_db(subcategories):
    try:
        conn = sqlite3.connect("../Executing/websites.db")
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(subcategories))
        cursor.execute(f"""
            SELECT headline, time_author, description, link, category, source
            FROM AllArticles 
            WHERE category IN ({placeholders})
        """, subcategories)
        articles = cursor.fetchall()
        conn.close()
        return articles
    except Exception as e:
        logger.error(f"Ошибка БД: {str(e)}")
        return []


def show_article(chat_id, index, m_id, filter, cd):
    try:

        data = user_articles.get(chat_id)
        logger.info(f"Попытка показа статьи #{index} для chat_id {chat_id}. Данные: {data}")


        if not data or index >= len(data['articles']):
            logger.warning("Нет данных или неверный индекс")
            return False

        article = data['articles'][index]
        if len(article) < 6:
            logger.error(f"Некорректная структура статьи: {article}")
            return False

        headline = article[0]
        time_author = article[1] if article[1] else "Не указано"
        description = article[2] if article[2] else "Описание отсутствует"
        link = article[3] if article[3] else "#"
        category = article[4] if article[4] else "Неизвестная категория"
        source = article[5] if article[5] else "Неизвестный источник"

        if int(filter) == 2:
            if source not in sources[2]:
                sources[2].append(source)

        if source in sources[int(filter)]:


            # Делаем заголовок кликабельной ссылкой
            clickable_headline = f'<a href="{link}">{headline}</a>'

            message_text = (
                f"📌 <b>Заголовок:</b> {clickable_headline}\n\n"
                f"⏳ <b>Время:</b> {time_author}\n\n"
                f"📝 <b>Описание:</b> {description[:300] + '...' if len(description) > 300 else description}\n\n"
                f"🏷️ <b>Категория:</b> {translation_dict.get(category, category)}\n\n"
                f"📰 <b>Источник:</b> {link}"
            )

            markup = types.InlineKeyboardMarkup()
            if index < len(data['articles']) - 1:
                markup.add(types.InlineKeyboardButton(text="Следующая →", callback_data=f"next_article_{cd}"))

            if index > 0:
                markup.add(types.InlineKeyboardButton(text="⟵ Предыдущая", callback_data=f"prev_article_{cd}"))

            markup.add(types.InlineKeyboardButton(text="В меню", callback_data="back_to_menu"))



            if not m_id:
                bot.send_message(
                    chat_id,
                    message_text,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )

            else:
                bot.edit_message_text(
                    message_text,
                    chat_id,
                    m_id,
                    parse_mode='HTML',
                    reply_markup=markup,
                    disable_web_page_preview=True
                )
                logger.info(f"Статья #{index} успешно отправлена")

            return True
        else:
            show_article(chat_id, index+1, m_id, filter, cd)
            return False

    except Exception as e:
        logger.error(f"Ошибка в show_article: {str(e)}")
        return False


@bot.message_handler(commands=["start"])
def start(message):
    try:
        menu_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Создать запрос")
        btn2 = types.KeyboardButton("Связаться с разработчиками")
        menu_markup.add(btn1, btn2)

        bot.send_message(
            message.chat.id,
            f"Привет, {message.chat.first_name}!\n"
            "Здесь вы можете посмотреть сбор публикаций по теме AI for Good за последний месяц 🚀.\n"
            "Это поможет исследователям отслеживать ключевые научные достижения и технологические тренды 💯",
            reply_markup=menu_markup
        )
        print(period(n = 1))
    except Exception as e:
        logger.error(f"Ошибка в обработчике start: {str(e)}")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        if message.text == "Создать запрос":
            category_markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="Экология", callback_data="Environmental")
            btn2 = types.InlineKeyboardButton(text="Безопасность", callback_data="Safety")
            btn3 = types.InlineKeyboardButton(text="Устойчивые города", callback_data="Sustainable Cities")
            btn4 = types.InlineKeyboardButton(text="Производство", callback_data="Manufacturing")
            btn5 = types.InlineKeyboardButton(text="Культура", callback_data="Culture")
            category_markup.add(btn1)
            category_markup.add(btn2)
            category_markup.add(btn3)
            category_markup.add(btn4)
            category_markup.add(btn5)
            bot.send_message(message.chat.id, "Выберите категорию", reply_markup=category_markup)
        elif message.text == "Связаться с разработчиками":
            back_to_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn = types.KeyboardButton("Вернуться в меню")
            back_to_menu.add(btn)
            bot.send_message(message.chat.id, "Связь с разработчиками: \n@alinesmakotina", reply_markup = back_to_menu)
        elif message.text == 'Вернуться в меню':
            start(message)
    except Exception as e:
        logger.error(f"Ошибка в обработчике handle_text: {str(e)}")


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        if call.data in ["Environmental", "Safety", "Sustainable Cities", "Manufacturing", "Culture"]:
            # Получаем список подкатегорий для выбранной категории
            subcategories = categories[call.data]

            # Показываем выбор периода
            markup = types.InlineKeyboardMarkup()
            for date in dates:
                btn = types.InlineKeyboardButton(date, callback_data=f"date_{date}_{call.data}")
                markup.add(btn)

            bot.send_message(
                chat_id,
                "Выберите период:",
                reply_markup=markup
            )

        elif call.data.startswith("date_"):

            markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('Отечественные', callback_data=f"filter_0_{call.data}")
            btn2 = types.InlineKeyboardButton('Иностранные', callback_data=f"filter_1_{call.data}")
            btn3 = types.InlineKeyboardButton('Любые', callback_data=f"filter_2_{call.data}")
            markup.add(btn1)
            markup.add(btn2)
            markup.add(btn3)
            bot.send_message(
                chat_id,
                "Выберите источнкики:",
                reply_markup=markup
            )

        elif call.data.startswith('filter'):
            __, filter,_, date, category = call.data.split("_")
            subcategories = categories[category]

            # Загружаем статьи
            articles = get_articles_from_db(subcategories)

            if not articles:
                bot.send_message(chat_id, "Статьи не найдены")
                return

            user_articles[chat_id] = {
                'category': category,
                'articles': articles,
                'current_index': 0
            }
            show_article(chat_id, 0, 0, filter, call.data)


        elif call.data[4::].startswith("_article"):
            user_data = user_articles.get(chat_id)
            if not user_data:
                return

            if call.data.startswith("next"):
                user_data['current_index'] += 1
            if call.data.startswith("prev"):
                user_data['current_index'] -= 1

            if user_data['current_index'] >= len(user_data['articles']):
                bot.send_message(chat_id, "Это последняя статья")
                user_data['current_index'] = len(user_data['articles']) - 1
                return

            print(call.data)
            show_article(chat_id, user_data['current_index'], call.message.id, filter= call.data.split('_')[3], cd = call.data[13::])

        elif call.data == "back_to_menu":
            start(call.message)
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")


if __name__ == '__main__':
    logger.info("Бот запущен")
    bot.polling(none_stop=True)
