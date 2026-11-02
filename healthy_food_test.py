import psycopg2

def calculate_price_healthy_food(item_id, base_price):
    try:
        conn = psycopg2.connect(
            dbname="healthy_food", user="postgres", password="123", host="localhost", port="5432"
        )
        cur = conn.cursor()
        
        # Считаем заказы за последний месяц
        query = """
            SELECT COUNT(*) 
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s 
            AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        cur.execute(query, (item_id,))
        result = cur.fetchone()
        orders_count = result[0] if result else 0
        cur.close()
        conn.close()
        
        # Условие скидки (для здорового питания дадим 10% скидки, если не заказывали)
        if orders_count == 0:
            return base_price * 0.90
        return base_price

    except psycopg2.Error as e:
        print(f"Ошибка БД: {e}")
        return None

# Тестовый запуск
if __name__ == "__main__":
    # Проверяем товар с ID=2 (например, Гречка), цена 120
    test_result = calculate_price_healthy_food(2, 120)
    print(f"Цена со скидкой для здорового питания: {test_result}")