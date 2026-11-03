import logging
import psycopg2
from psycopg2 import pool

logging.basicConfig(filename='app_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class Database:
    def __init__(self):
        self.connection_pool = None
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 10,
                dbname="healthy_food",
                user="postgres",
                password="123", # <--- ВАШ ПАРОЛЬ
                host="localhost",
                port="5432",
                client_encoding='UTF8'
            )
            print("Пул соединений успешно создан.")
        except Exception as e:
            logging.error(f"Ошибка создания пула: {e}")

    def get_connection(self):
        if self.connection_pool is None: return None
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()

    def execute_query(self, sql, params=None):
        conn = self.get_connection()
        if not conn: return []
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            result = cur.fetchall()
            cur.close()
            return result
        except Exception as e:
            logging.error(f"Ошибка SELECT: {e}")
            print(f"Ошибка: {e}")
            return []
        finally:
            self.release_connection(conn)

    def get_categories(self):
        query = "SELECT DISTINCT name FROM categories ORDER BY name"
        result = self.execute_query(query)
        return [row[0] for row in result] if result else []

    def get_manufacturers(self):
        query = "SELECT DISTINCT manufacturer FROM products WHERE manufacturer IS NOT NULL ORDER BY manufacturer"
        result = self.execute_query(query)
        return [row[0] for row in result] if result else []