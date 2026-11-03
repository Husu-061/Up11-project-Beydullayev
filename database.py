import logging
from psycopg2 import pool

logging.basicConfig(
    filename='app_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class Database:
    """Класс для управления подключением к базе данных PostgreSQL через пул соединений."""

    def __init__(self):
        """Инициализирует пул соединений с базой данных."""
        self.connection_pool = None
        try:
            self.connection_pool = pool.SimpleConnectionPool(
                1, 10,
                dbname="healthy_food",
                user="postgres",
                password="123",  # <--- ВАШ ПАРОЛЬ
                host="localhost",
                port="5432",
                client_encoding='UTF8'
            )
            print("Пул соединений успешно создан.")
        except Exception as e:
            logging.error(f"Ошибка создания пула: {e}")

    def get_connection(self):
        """Возвращает соединение из пула."""
        if self.connection_pool is None:
            return None
        return self.connection_pool.getconn()

    def release_connection(self, conn):
        """Возвращает соединение обратно в пул."""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)

    def close_all(self):
        """Закрывает все соединения в пуле."""
        if self.connection_pool:
            self.connection_pool.closeall()

    def execute_query(self, sql, params=None):
        """Выполняет SELECT-запрос и возвращает список строк."""
        conn = self.get_connection()
        if not conn:
            return []
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

    def execute_update(self, sql, params=None):
        """Выполняет INSERT/UPDATE/DELETE запрос. Возвращает True при успехе."""
        conn = self.get_connection()
        if not conn:
            return False
        try:
            cur = conn.cursor()
            cur.execute(sql, params or ())
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            logging.error(f"Ошибка UPDATE: {e}")
            conn.rollback()
            return False
        finally:
            self.release_connection(conn)

    def get_categories(self):
        """Возвращает список уникальных названий категорий для фильтра."""
        query = "SELECT DISTINCT name FROM categories ORDER BY name"
        result = self.execute_query(query)
        return [row[0] for row in result] if result else []

    def get_manufacturers(self):
        """Возвращает список уникальных производителей для фильтра."""
        query = "SELECT DISTINCT manufacturer FROM products WHERE manufacturer IS NOT NULL ORDER BY manufacturer"
        result = self.execute_query(query)
        return [row[0] for row in result] if result else []

    def get_products(self):
        """Возвращает список товаров с категориями и общим остатком на складе."""
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
