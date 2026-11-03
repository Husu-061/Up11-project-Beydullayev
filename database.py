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
            # ДЗ: Настроен пул с minconn=1, maxconn=10
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

    # ДЗ: Универсальный метод для SELECT
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
            return []
        finally:
            self.release_connection(conn)

    # ДЗ: Универсальный метод для INSERT/UPDATE/DELETE
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

    # ДЗ: Функция обновления цены
    def update_price(self, product_id, new_price):
        if not isinstance(new_price, (int, float)) or new_price <= 0:
            print("Ошибка: цена должна быть больше нуля")
            logging.error(f"Попытка установить некорректную цену: {new_price}")
            return False
        
        success = self.execute_update(
            "UPDATE products SET price = %s WHERE product_id = %s",
            (new_price, product_id)
        )
        if success:
            print(f"Цена для товара ID {product_id} обновлена на {new_price}")
        return success

    def get_products(self):
        # Используем наш новый универсальный метод
        query = """
            SELECT p.product_id, c.name, p.name, p.price, p.stock_quantity, p.image_path
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            ORDER BY p.product_id
        """
        return self.execute_query(query)