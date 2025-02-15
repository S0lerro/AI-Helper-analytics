import sqlite3

# Функция для подключения к базе данных
def connect_db():
    return sqlite3.connect('websites.db')

# Функция для выполнения SQL-запроса
def execute_query(query):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query)
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
            if result:
                for row in result:
                    print(row)
            else:
                print("Нет данных.")
        else:
            conn.commit()
            print("Запрос выполнен успешно.")
    except sqlite3.Error as e:
        print(f"Ошибка SQL: {e}")
    finally:
        conn.close()

# Основной цикл для ввода запросов
def main():
    print("Добро пожаловать в консоль запросов SQL!")
    print("Для выхода из программы введите 'exit'.")
    
    while True:
        # Запрос от пользователя
        query = input("Введите SQL-запрос: ")
        
        if query.lower() == 'exit':
            print("Выход из программы.")
            break
        
        execute_query(query)

if __name__ == "__main__":
    main()
