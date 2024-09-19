import sqlite3


class SQLiteCRUD:
    def __init__(self, db_name):
        """Инициализация подключения к базе данных."""
        self.db_name = db_name
        with sqlite3.connect(db_name) as self.connection:
          self.cursor = self.connection.cursor()

    def create_table(self, table_name, columns):
        """Создание таблицы."""
        columns_definition = ', '.join(f"{col_name} {col_type}" for col_name, col_type in columns.items())
        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definition});"
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def insert(self, table_name, **kwargs):
        """Вставка новой записи в таблицу."""
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join('?' for _ in kwargs)
        values = tuple(kwargs.values())
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        self.cursor.execute(insert_query, values)
        self.connection.commit()

    def read(self, table_name, columns='*', where_clause=None):
        """Чтение записей из таблицы."""
        if where_clause:
            select_query = f"SELECT {columns} FROM {table_name} WHERE {where_clause};"
        else:
            select_query = f"SELECT {columns} FROM {table_name};"
        self.cursor.execute(select_query)
        results = self.cursor.fetchall()
        return results if results else None
    
    def update(self, table_name, set_clause, where_clause):
        """Обновление записей в таблице."""
        update_query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"
        self.cursor.execute(update_query)
        self.connection.commit()

    def delete(self, table_name, where_clause,where_product):
        """Удаление записей из таблицы."""
        delete_query = f"DELETE FROM {table_name} WHERE {where_clause} AND {where_product};"
        self.cursor.execute(delete_query)
        self.connection.commit()

    def close(self):
        """Закрытие подключения к базе данных."""
        self.connection.close()


decs = 'main_app_descriptionmod'
usermod = 'main_app_usermod'
cat = 'main_app_categirymod'
but = 'main_app_buttonmod'
# Пример использования
if __name__ == "__main__":
    db = SQLiteCRUD('db.sqlite3')

    all_users_data = db.read(usermod)
    false_users_data = db.read(usermod,where_clause='payment = 1')
    true_users_data = db.read(usermod,where_clause='payment = 0')
    for i in false_users_data:
        print(i)
 
    # Создание таблицы
    # db.create_table('main_app_userscarts', {
    #     'id': 'INTEGER PRIMARY KEY AUTOINCREMENT',
    #     'name': 'TEXT NOT NULL',
    #     'age': 'INTEGER'
    # })

    # Вставка записей
    # db.insert('main_app_userscarts', telegram_id='',name='Alice', phone_number=30,product_id='')

    # Чтение записей
    # for i in db.read('main_app_productmod',where_clause='category_id = 1'):
    #     print(i)
    # for i in db.read(usermod,where_clause=f'telegram_id = {767560862}'):
    #     print(i[7])
    # a = db.read(usermod,where_clause=f'telegram_id = {767560862}')
    # print(a[0][7])

    # Обновление записей
    # db.update('main_app_userscarts', 'age = 31', 'name = "Alice"')
    # for i in  db.read('main_app_productmod'):
    #   print(i)
    # Удаление записей

    # db.delete('main_app_userscarts', f'telegram_id = "{n}"',f'productr_id = "{k}"')

    # Закрытие подключения
    # db.close()
