import sqlite3


def prepare_database() -> None:
    '''Функция создаёт основные таблицы программы: \n 
    activities - таблица содержит информацию о количестве запросов на каждый день \n
    anomalies - таблица содержит аномалии с их типом и датой'''


    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS activities (
        day INTEGER PRIMARY KEY,
        requests_cnt INTEGER
    ) ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anomalies (
        id INTEGER PRIMARY KEY,
        anomaly_type BOOLEAN,
        day INTEGER
    ) ''')
    conn.commit()
    conn.close()

def create_monthly_tables() -> None:
    '''Функция создаёт вспомогательные таблицы программы: \n 
    monthly_activities - таблица содержит информацию о колиечстве запросов на каждый месяц \n
    monthly_anomalies - таблица содержит аномалии с их типом и датой'''
    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS monthly_activities (
        day INTEGER PRIMARY KEY,
        requests_cnt INTEGER
    ) ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS monthly_anomalies (
        id INTEGER PRIMARY KEY,
        anomaly_type BOOLEAN,
        month INTEGER
    ) ''')
    conn.commit()
    conn.close()

def table_empty(table_name : str) -> bool:
    '''Проверка, пуста ли таблица'''
    # Подключаемся к базе данных
    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    
    # Выполняем SQL-запрос для подсчета строк в таблице
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    conn.close()
    return (row_count == 0)

def get_acivities_from_dataset(url : str) -> list[int]:
    '''Получение массива с количеством активностей на каждом временном промежутке 
    (ежедневно или ежемесячно) заданного сайта'''
    return [0]

def find_amonalies(activities : list[int]):
    '''Основной алгоритм нахождения аномалий'''
    return [[False, 0]]

def insert_activs_into_db(numbers):
    '''Занесение массива с количеством ежедневных запросов на сайт в базу данных'''
    # Подключаемся к базе данных (если она не существует, она будет создана)
    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    # Вставляем данные в таблицу
    for key, value in enumerate(numbers):
        if 0 <= key <= 354:  # Проверяем, чтобы ключ был в нужном диапазоне
            cursor.execute(f'''
            INSERT OR REPLACE INTO activities (day, requests_cnt) VALUES (?, ?)''', (key, value))
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def insert_montly_activs_into_db(numbers):
    '''Занесение массива с количеством ежемесячных запросов на сайт в базу данных'''
    # Подключаемся к базе данных (если она не существует, она будет создана)
    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    # Вставляем данные в таблицу
    for key, value in enumerate(numbers):
        if 0 <= key <= 11:  # Проверяем, чтобы ключ был в нужном диапазоне
            cursor.execute(f'''
            INSERT OR REPLACE INTO monthly_activities (month, requests_cnt) VALUES (?, ?)''', (key, value))
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def insert_anoms_into_db(numbers):
    '''Занесение массива с ежедневными аномалиями в базу данных'''
    # Подключаемся к базе данных (если она не существует, она будет создана)
    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    # Вставляем данные в таблицу
    for key, value in enumerate(numbers):
        if 0 <= key <= 354:  # Проверяем, чтобы ключ был в нужном диапазоне
            cursor.execute(f'''
            INSERT OR REPLACE INTO anomalies (id, anomaly_type, day) VALUES (?, ?)''', (key, value[0], value[1]))
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def insert_montly_anoms_into_db(numbers):
    '''Занесение массива с ежемесячными аномалиями в базу данных'''
    # Подключаемся к базе данных (если она не существует, она будет создана)
    conn = sqlite3.connect('numbers.db')
    cursor = conn.cursor()
    # Вставляем данные в таблицу
    for key, value in enumerate(numbers):
        if 0 <= key <= 11:  # Проверяем, чтобы ключ был в нужном диапазоне
            cursor.execute(f'''
            INSERT OR REPLACE INTO montly_anomalies (id, anomaly_type, month) VALUES (?, ?)''', (key, value[0], value[1]))
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()

def main():
    ulr_adress = input()
    prepare_database()
    activs = get_acivities_from_dataset(ulr_adress)
    anoms = find_amonalies(activs)
    insert_activs_into_db(activs)
    insert_anoms_into_db(anoms)
    
    if table_empty('anomalies'):
        conn = sqlite3.connect('numbers.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM anomalies")
        rows = cursor.fetchall()
        conn.close()
        montly_activies = [sum(rows[1][30*i:30*(i+1)]) // 12  for i in range(12)]
        montly_anoms = find_amonalies(montly_activies)
        insert_montly_activs_into_db(montly_activies)
        insert_montly_anoms_into_db(montly_anoms)
        if table_empty('montly_anomalies'):
            print('Никаких аномалий нет и не предвидется')
            return
        print('Никаких аномалий сейчас нет, но видны следующие сезонные аномалии:\n')
        for key, value in montly_anoms:
            if key == False:
                print(f'Временная аномалия в {value} месяц')
            else:
                print(f'Хакерская аномалия в {value} месяц')
        return
    for key, value in anoms:
        if key == False:
            print(f'Временная аномалия в {value} месяц')
        else:
            print(f'Хакерская аномалия в {value} месяц')
    return
    
main()
