from calendar import month

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
    "Environmental": [
        "Waste Management",
        "Climate Risks",
        "Greenhouse Gas Emissions",
        "Air Pollution",
        "Energy Efficiency and Renewable",
        "Hazardous Materials Management",
        "Soil and Groundwater Impact",
        "Natural Resources",
        "Planning Limitations",
        "Landscape Transformation",
        "Land Rehabilitation",
        "Biodiversity",
        "Animal Welfare",
        "Emergencies (Environmental)",
        "Environmental Management",
        "Supply Chain (Environmental)",
        "Physical Impacts",
        "Land Acquisition and Resettlement (Environmental)",
        "Wastewater Management",
        "Water Consumption",
        "Surface Water Pollution"
    ],
    "Social": [
        "Emergencies (Social)",
        "Employee Health and Safety",
        "Land Acquisition and Resettlement (Social)",
        "Product Safety and Quality",
        "Indigenous People",
        "Human Rights",
        "Communities Health and Safety",
        "Freedom of Association and Right to Organise",
        "Minimum Age and Child Labor",
        "Data Safety",
        "Forced Labor",
        "Discrimination",
        "Cultural Heritage",
        "Supply Chain (Social)",
        "Retrenchment",
        "Labor Relations Management"
    ]
}
dates = ['Эта неделя', 'Прошлая неделя', 'За весь месяц']

translation_dict = {
    "Environmental": "Окружающая среда",
    "Social": "Общество",
    "Waste Management": "Управление отходами",
    "Climate Risks": "Климатические риски",
    "Greenhouse Gas Emissions": "Выбросы парниковых газов",
    "Air Pollution": "Загрязнение воздуха",
    "Energy Efficiency and Renewable": "Энергоэффективность и возобновляемая энергия",
    "Hazardous Materials Management": "Управление опасными материалами",
    "Soil and Groundwater Impact": "Воздействие на почву и грунтовые воды",
    "Natural Resources": "Природные ресурсы",
    "Planning Limitations": "Ограничения планирования",
    "Landscape Transformation": "Преобразование ландшафта",
    "Land Rehabilitation": "Восстановление земель",
    "Biodiversity": "Биоразнообразие",
    "Animal Welfare": "Благополучие животных",
    "Emergencies (Environmental)": "Экологические чрезвычайные ситуации",
    "Environmental Management": "Управление окружающей средой",
    "Supply Chain (Environmental)": "Цепочка поставок (экологическая)",
    "Physical Impacts": "Физические воздействия",
    "Land Acquisition and Resettlement (Environmental)": "Захват и переселение земель (экологическое)",
    "Wastewater Management": "Управление сточными водами",
    "Water Consumption": "Потребление воды",
    "Surface Water Pollution": "Загрязнение поверхностных вод",
    "Emergencies (Social)": "Социальные чрезвычайные ситуации",
    "Employee Health and Safety": "Здоровье и безопасность сотрудников",
    "Land Acquisition and Resettlement (Social)": "Захват и переселение земель (социальное)",
    "Product Safety and Quality": "Безопасность и качество продукции",
    "Indigenous People": "Коренные народы",
    "Human Rights": "Права человека",
    "Communities Health and Safety": "Здоровье и безопасность сообществ",
    "Freedom of Association and Right to Organise": "Свобода ассоциации и право на организацию",
    "Minimum Age and Child Labor": "Минимальный возраст и детский труд",
    "Data Safety": "Безопасность данных",
    "Forced Labor": "Принудительный труд",
    "Discrimination": "Дискриминация",
    "Cultural Heritage": "Культурное наследие",
    "Supply Chain (Social)": "Цепочка поставок (социальная)",
    "Retrenchment": "Сокращение штата",
    "Labor Relations Management": "Управление трудовыми отношениями"
}

t = open('../TOKEN.txt')
TOKEN = t.read().strip()
t.close()
bot = telebot.TeleBot(TOKEN)


def get_articles_from_db(subcategories):
    try:
        conn = sqlite3.connect("../Executing/websites.db")
        cursor = conn.cursor()
        placeholders = ",".join(["?"] * len(subcategories))
        cursor.execute(f"""
            SELECT headline, time_author, description, link, category
            FROM AllArticles 
            WHERE category IN ({placeholders})
        """, subcategories)
        articles = cursor.fetchall()
        conn.close()
        return articles
    except Exception as e:
        logger.error(f"Ошибка БД: {str(e)}")
        return []


def show_article(chat_id, index, m_id):
    try:
        data = user_articles.get(chat_id)
        logger.info(f"Попытка показа статьи #{index} для chat_id {chat_id}. Данные: {data}")

        if not data or index >= len(data['articles']):
            logger.warning("Нет данных или неверный индекс")
            return False

        article = data['articles'][index]
        if len(article) < 5:
            logger.error(f"Некорректная структура статьи: {article}")
            return False

        headline = article[0]
        time_author = article[1] if len(article) > 1 else "Не указано"
        description = article[2] if len(article) > 2 else "Описание отсутствует"
        link = article[3] if len(article) > 3 else "#"
        category = article[4] if len(article) > 4 else "Неизвестная категория"
        source = article[5] if len(article) > 5 else "Неизвестный источник"


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
            markup.add(types.InlineKeyboardButton(text="Следующая →", callback_data="next_article"))

        if index > 0:
            markup.add(types.InlineKeyboardButton(text="⟵ Предыдущая", callback_data="prev_article"))

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
            f"Привет, {message.from_user.first_name}!\n"
            "Здесь вы можете посмотреть сбор публикаций по теме AI for Good за последний месяц 🚀.\n"
            "Это поможет исследователям отслеживать ключевые научные достижения и технологические тренды 💯",
            reply_markup=menu_markup
        )
    except Exception as e:
        logger.error(f"Ошибка в обработчике start: {str(e)}")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        if message.text == "Создать запрос":
            category_markup = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text="Окружающая среда", callback_data="Environmental")
            btn2 = types.InlineKeyboardButton(text="Общество", callback_data="Social")
            category_markup.add(btn1, btn2)
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

        if call.data in ["Environmental", "Social"]:
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
            _, date, category = call.data.split("_")
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
            show_article(chat_id, 0, 0)

        elif call.data[4::] == "_article":
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

            show_article(chat_id, user_data['current_index'], call.message.id)

        elif call.data == "back_to_menu":
            start(call.message)
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")


if __name__ == '__main__':
    logger.info("Бот запущен")
    bot.polling(none_stop=True)
