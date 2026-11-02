from database import Database

db = Database()
products = db.get_products()
print(f"Метод get_products() вернул строк: {len(products)}")
if products:
    print(f"Первый товар: {products[0]}")
db.close_all()