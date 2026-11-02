import psycopg2
from discount import calculate_price  # Импортируем нашу функцию из discount.py

# Подключение к БД
conn = psycopg2.connect(
    dbname="healthy_food",
    user="postgres",
    password="123", 
    host="localhost",
    port="5432"
)
cur = conn.cursor()

# Выбираем все товары
cur.execute("SELECT product_id, name, price FROM products LIMIT 5") # Берем первые 5 для примера
products = cur.fetchall()

print(f"{'ID':<3} | {'Товар':<25} | {'Цена':<8} | {'Итоговая цена':<15} | Скидка?")
print("-" * 75)

for row in products:
    product_id, name, price = row
    final_price = calculate_price(product_id, float(price))
    
    # Проверяем, что функция не вернула None (ошибку)
    if final_price is not None:
        discount = "Да (25%)" if final_price < float(price) else "Нет"
    else:
        discount = "Ошибка"
    # Обрезаем длинное название, чтобы таблица была ровной
    short_name = name[:25]
    
    print(f"{product_id:<3} | {short_name:<25} | {price:<8} | {final_price:<15} | {discount}")

cur.close()
conn.close()