import logging
import psycopg2
from psycopg2 import pool

# ДЗ: Логирование ошибок в файл
logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

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
            print(f"Ошибка БД: {e}")
            logging.error(f"Ошибка создания пула: {e}")

    def get_connection(self):
        if self.connection_pool is None:
            return None
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_all(self):
        if self.connection_pool:
            self.connection_pool.closeall()
            print("Все соединения закрыты.")

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
            logging.error(f"Ошибка выполнения SELECT: {e}")
            print(f"Ошибка SELECT: {e}")
            return []
        finally:
            self.release_connection(conn)

    def execute_update(self, sql, params=None):
        conn = self.get_connection()
        if not conn: return False
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка выполнения UPDATE/INSERT: {e}")
            conn.rollback()
            return False
        finally:
            self.release_connection(conn)

    def get_products(self):
        # ЗАДАНИЕ 1 и 2: Правильный запрос с подсчетом остатков из stock_items
        query = """
            SELECT p.product_id, c.name, p.name, p.price, p.image_path,
                   COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            GROUP BY p.product_id, c.name, p.name, p.price, p.image_path
            ORDER BY p.product_id
        """
        return self.execute_query(query)