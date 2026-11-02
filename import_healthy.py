import csv
import psycopg2

def import_healthy_food():
    try:
        conn = psycopg2.connect(
            dbname="healthy_food", user="postgres", password="123", 
            host="localhost", port="5432", client_encoding='UTF8'
        )
        cur = conn.cursor()

        # Открываем наш новый правильный CSV
        with open('healthy_products.csv', 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f)
            
            count = 0
            for row in reader:
                # Берем только нужные нам колонки
                category_name = row.get('Категория', '').strip()
                product_name = row.get('Наименование товара', '').strip()
                price_str = row.get('Цена', '0').replace(',', '.').strip()

                if not category_name or not product_name:
                    continue

                # 1. Добавляем категорию в базу (если ее еще нет)
                cur.execute(
                    "INSERT INTO categories (name) VALUES (%s) ON CONFLICT (name) DO NOTHING",
                    (category_name,)
                )
                
                # Получаем ID категории
                cur.execute("SELECT category_id FROM categories WHERE name = %s", (category_name,))
                result = cur.fetchone()
                category_id = result[0] if result else None

                # 2. Добавляем сам товар
                if category_id and product_name and price_str:
                    try:
                        price = float(price_str)
                        cur.execute(
                            "INSERT INTO products (category_id, name, price, stock_quantity) VALUES (%s, %s, %s, %s)",
                            (category_id, product_name, price, 100) # 100 шт. на склад
                        )
                        count += 1
                    except ValueError:
                        print(f"Ошибка в цене у товара: {product_name}")

        conn.commit()
        print(f"Успешно загружено {count} товаров здорового питания!")
        
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    import_healthy_food()