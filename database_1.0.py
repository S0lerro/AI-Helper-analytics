import pandas as pd
import sqlite3

# Загрузка данных из Excel (без заголовков)
df = pd.read_excel('websites_data.xlsx', header=None)

# Подключение к базе данных SQLite
conn = sqlite3.connect('websites.db')
cursor = conn.cursor()

# Удаление таблицы, если она существует (пересоздаём таблицу)
cursor.execute('DROP TABLE IF EXISTS websites')

# Создание таблицы в базе данных
cursor.execute('''
CREATE TABLE websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_name TEXT,
    url TEXT,
    gost_link TEXT,
    site_info TEXT
)
''')

# Вставка данных в таблицу
for index, row in df.iterrows():
    site_name = row[0]        # Первая колонка: Имя сайта
    url = row[1]              # Вторая колонка: Ссылка
    gost_link = row[2]        # Третья колонка: Ссылка по ГОСТу
    site_info = row[3]        # Четвертая колонка: Информация

    # Вставка данных в базу данных
    cursor.execute('''
    INSERT INTO websites (site_name, url, gost_link, site_info) 
    VALUES (?, ?, ?, ?)
    ''', (site_name, url, gost_link, site_info))

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()

print("Таблица успешно пересоздана и данные импортированы.")
