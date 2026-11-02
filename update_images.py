import csv
import psycopg2

def update_images():
    conn = psycopg2.connect(
        dbname="healthy_food", user="postgres", password="123", # <--- ВАШ ПАРОЛЬ
        host="localhost", port="5432", client_encoding='UTF8'
    )
    cur = conn.cursor()

    # Открываем исходный CSV
    try:
        with open('healthy_products.csv', 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.DictReader(f)
            count = 0
            
            for row in reader:
                product_name = row.get('Наименование товара', '').strip()
                image_name = row.get('Изображение', '').strip()
                
                if product_name and image_name:
                    # Обновляем путь к картинке для товара с таким именем
                    cur.execute(
                        "UPDATE products SET image_path = %s WHERE name = %s",
                        (image_name, product_name)
                    )
                    count += cur.rowcount
                    
        conn.commit()
        print(f"Успешно обновлено путей к картинкам: {count}")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    update_images()