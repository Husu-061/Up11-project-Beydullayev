import psycopg2
from psycopg2 import pool

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
            self.connection_pool = None

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

    def get_products(self):
        conn = self.get_connection()
        if not conn: return []
        try:
            cur = conn.cursor()
            query = """
                SELECT p.product_id, c.name, p.name, p.price, p.stock_quantity, p.image_path
                FROM products p
                JOIN categories c ON p.category_id = c.category_id
                ORDER BY p.product_id
            """
            cur.execute(query)
            products = cur.fetchall()
            cur.close()
            return products
        except Exception as e:
            print(f"Ошибка при получении товаров: {e}")
            return []
        finally:
            self.release_connection(conn)