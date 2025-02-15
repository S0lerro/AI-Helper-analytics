import pandas as pd
import sqlite3

# Загрузка данных из Excel (без заголовков)
df = pd.read_excel('websites_data.xlsx', header=None)

# Подключение к базе данных SQLite
conn = sqlite3.connect('websites.db')
cursor = conn.cursor()

# Проверка, существует ли таблица, если нет, создаем ее
cursor.execute('''
CREATE TABLE IF NOT EXISTS websites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_name TEXT,
    time_author TEXT,
    description TEXT,
    link TEXT
)
''')

# Вставка данных в таблицу (добавляем только новые данные)
for index, row in df.iterrows():
    site_name = row[0]        # Первая колонка: Заголовок
    time_author = row[1]              # Вторая колонка: Время и автор публикации
    description = row[2]        # Третья колонка: описание
    link = row[3]        # Четвертая колонка: ссылка на сайт

    # Вставка данных в базу данных
    cursor.execute('''
    INSERT INTO websites (site_name, time_author, description, link) 
    VALUES (?, ?, ?, ?)
    ''', (site_name, time_author, description, link))

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()

print("Данные успешно добавлены в таблицу.")
