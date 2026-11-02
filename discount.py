import psycopg2

def calculate_price(product_id, base_price):
    if not isinstance(product_id, int):
        print("Ошибка: product_id должен быть целым числом")
        return None
    if not isinstance(base_price, (int, float)) or base_price <= 0:
        print("Ошибка: base_price должен быть положительным числом")
        return None

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname="healthy_food", user="postgres", password="123", # <--- ВАШ ПАРОЛЬ
            host="localhost", port="5432", client_encoding='UTF8'
        )
        cur = conn.cursor()
        
        
        query = """
            SELECT COUNT(*) 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        cur.execute(query, (product_id,))
        result = cur.fetchone()
        
        if result is None:
            print("Ошибка: нет результата")
            return None
            
        orders_count = result[0] if result else 0
        
        if orders_count == 0:
            return base_price * 0.75
        return base_price

    except Exception as e:
        print(f"Ошибка БД: {e}")
        return None
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()

def add_product(name, price, category_id):
    # 1. Проверка входных данных
    if not name or not isinstance(name, str) or name.strip() == "":
        print("Ошибка: имя не может быть пустым")
        return False
        
    if not isinstance(price, (int, float)) or price <= 0:
        print("Ошибка: цена должна быть > 0")
        return False
        
    if not isinstance(category_id, int):
        print("Ошибка: category_id должен быть числом")
        return False

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname="healthy_food", user="postgres", password="123", # <--- ВАШ ПАРОЛЬ
            host="localhost", port="5432", client_encoding='UTF8'
        )
        cur = conn.cursor()
        

        query = "INSERT INTO products (name, price, category_id, stock_quantity) VALUES (%s, %s, %s, %s)"
        cur.execute(query, (name, price, category_id, 100))
        

        conn.commit()
        print(f"Товар '{name}' успешно добавлен!")
        return True

    except psycopg2.Error as e:
        if conn:
            conn.rollback() # Откатываем изменения при ошибке
        print(f"Ошибка БД при вставке: {e}")
        return False
    finally:
        if cur is not None: cur.close()
        if conn is not None: conn.close()


# ==========================================
# ЗАДАНИЕ 5.2: Тестовые запуски
# ==========================================
if __name__ == "__main__":
    print("--- Тесты функции add_product ---")
    
    # Тест 1: Пустое имя
    add_product("", 1000, 1)
    
    # Тест 2: Цена меньше нуля
    add_product("Часы", -100, 1)
    
    # Тест 3: Категории с ID 99999 не существует в базе
    add_product("Часы", 1000, 99999)
    
    # Тест 4: Всё правильно (категория 1 существует)
    add_product("Здоровый снек", 150, 1)