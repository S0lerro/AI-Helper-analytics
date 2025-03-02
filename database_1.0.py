import pandas as pd
import sqlite3

# Загрузка данных из CSV файла
df = pd.read_csv('FerraFrame.csv')

# Подключение к базе данных SQLite
conn = sqlite3.connect('websites.db')
cursor = conn.cursor()

# Проверка, существует ли таблица FerraFrame, если нет, создаем ее
cursor.execute('''
CREATE TABLE IF NOT EXISTS FerraFrame (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    headline TEXT,
    time_author TEXT,
    description TEXT,
    link TEXT
)
''')

# Вставка данных в таблицу FerraFrame (добавляем только новые данные)
for index, row in df.iterrows():
    headline = row['Заголовок']        # Первая колонка: Заголовок
    time_author = row['Время и автор публикации']              # Вторая колонка: Время и автор публикации
    description = row['Описание']        # Третья колонка: Описание
    link = row['Ссылка']        # Четвертая колонка: Ссылка на сайт

    # Вставка данных в таблицу FerraFrame
    cursor.execute('''
    INSERT INTO FerraFrame (headline, time_author, description, link) 
    VALUES (?, ?, ?, ?)
    ''', (headline, time_author, description, link))

# Сохранение изменений и закрытие подключения
conn.commit()
conn.close()

print("Данные успешно добавлены в таблицу FerraFrame.")
