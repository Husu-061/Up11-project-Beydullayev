import psycopg2

def calculate_price_healthy_food(item_id, base_price):

    if not isinstance(item_id, int):
        print("Ошибка: ID товара должен быть целым числом")
        return None
        
    if not isinstance(base_price, (int, float)):
        print("Ошибка: Базовая цена должна быть числом")
        return None
        
    if base_price <= 0:
        print("Ошибка: Базовая цена должна быть больше нуля")
        return None

    conn = None
    cur = None
    
    try:

        conn = psycopg2.connect(
            dbname="healthy_food", 
            user="postgres", 
            password="123",  
            host="localhost", 
            port="5432", 
            client_encoding='UTF8'
        )
        cur = conn.cursor()
        
        # Считаем количество заказов за последний месяц
        query = """
            SELECT COUNT(*) 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        cur.execute(query, (item_id,))
        result = cur.fetchone()
        
        if result is None:
            print("Ошибка: нет результата из БД")
            return None
            
        orders_count = result[0]
        

        if orders_count == 0:
            return base_price * 0.90  # Даем скидку 10%
        return base_price


    except Exception as e:
        print(f"Ошибка БД: {e}")
        return None
        

    finally:
        if cur is not None:
            cur.close()
        if conn is not None:
            conn.close()



if __name__ == "__main__":
    print("--- Тесты для 'Мира здорового питания' ---")
    
    print("\n1. Неверный ID (строка):")
    calculate_price_healthy_food("abc", 1000)
    
    print("\n2. Неверная цена (отрицательная):")
    calculate_price_healthy_food(1, -500)
    
    print("\n3. Неверная цена (None):")
    calculate_price_healthy_food(1, None)
    
    print("\n4. Успешный запрос (ID=1, цена=500):")
    res = calculate_price_healthy_food(1, 500)
    print(f"Итоговая цена: {res}")