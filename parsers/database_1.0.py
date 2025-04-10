import pandas as pd
import sqlite3

df = pd.read_csv('svmain.csv')

conn = sqlite3.connect('websites.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS AllArticles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    headline TEXT,
    time_author TEXT,
    description TEXT,
    link TEXT,
    category TEXT
)
''')

for index, row in df.iterrows():
    headline = row['Заголовок']  # Первая колонка: Заголовок
    time_author = row['Время публикации']  # Вторая колонка: Время публикации
    description = row['Описание']  # Третья колонка: Описание
    link = row['Ссылка']  # Четвертая колонка: Ссылка на сайт
    category = row['Категория']

    cursor.execute('''
    INSERT INTO AllArticles (headline, time_author, description, link, category) 
    VALUES (?, ?, ?, ?, ?)
    ''', (headline, time_author, description, link, category))

conn.commit()
conn.close()

print("Данные успешно добавлены в таблицу AllArticles.")
