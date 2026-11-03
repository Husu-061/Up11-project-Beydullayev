import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                               QWidget, QHBoxLayout, QScrollArea, QPushButton, QCheckBox, QComboBox) 
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database

# ДЗ: Кэш для картинок
image_cache = {}

def calculate_discount(old_price, new_price):
    if old_price == 0: return 0
    return (old_price - new_price) / old_price * 100

# ДЗ: Возвращает кортеж и выводит название товара
def calculate_price(product_id, old_price, cursor):
    try:
        cursor.execute("SELECT name FROM products WHERE product_id = %s", (product_id,))
        name_res = cursor.fetchone()
        product_name = name_res[0] if name_res else "Неизвестный товар"
        
        query = """
            SELECT COUNT(*) FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        orders_count = result[0] if result else 0
        
        if orders_count == 0:
            final_price = float(old_price) * 0.75
        else:
            final_price = float(old_price)
            
        discount_size = float(old_price) - final_price
        return final_price, discount_size
    except Exception as e:
        return float(old_price), 0.0

def create_card(product, discount, new_price): 
    card = QWidget()
    card.setObjectName("productCard")
    
    card_layout = QHBoxLayout()
    card_layout.setContentsMargins(10, 10, 10, 10)
    
    # ДЗ: Кэширование изображений
    image_path = product[5]
    if image_path not in image_cache:
        if image_path is not None and os.path.exists(f"Images/{image_path}"):
            image_cache[image_path] = QPixmap(f"Images/{image_path}")
        else:
            image_cache[image_path] = QPixmap("resources/picture.png")
    
    img_label = QLabel()
    img_label.setFixedSize(100, 100)
    img_label.setStyleSheet("border: 1px solid #ddd; background-color: #fff;")
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    pixmap = image_cache[image_path]
    if not pixmap.isNull():
        img_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    card_layout.addWidget(img_label)
    
    text_layout = QVBoxLayout()
    name_label = QLabel(f"Наименование: {product[2]}")
    name_label.setStyleSheet("font-weight: bold; font-size: 16px; border: none; background: transparent;")
    category_label = QLabel(f"Категория: {product[1]}")
    category_label.setStyleSheet("border: none; background: transparent;")
    stock_label = QLabel(f"В наличии: {product[4]} шт.")
    stock_label.setStyleSheet("border: none; background: transparent;")
    text_layout.addWidget(name_label)
    text_layout.addWidget(category_label)
    text_layout.addWidget(stock_label)
    card_layout.addLayout(text_layout)
    
    old_price = float(product[3])
    price_box = QVBoxLayout()
    price_box.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    old_price_label = QLabel(f"<s>{old_price:.2f} ₽</s>")
    old_price_label.setStyleSheet("color: red; border: none; background: transparent;")
    old_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    
    new_price_label = QLabel(f"{new_price:.2f} ₽")
    new_price_label.setStyleSheet("color: black; font-weight: bold; font-size: 20px; border: none; background: transparent;")
    new_price_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    
    discount_label = QLabel(f"-{int(discount)}%")
    discount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    if discount > 30:
        discount_label.setStyleSheet("color: #E65100; font-weight: bold; border: none; background: transparent;")
    elif discount > 15:
        discount_label.setStyleSheet("color: #2E8B57; font-weight: bold; border: none; background: transparent;")
    else:
        discount_label.hide()

    if discount > 0:
        old_price_label.show()
    else:
        old_price_label.hide()
        
    price_box.addWidget(old_price_label)
    price_box.addWidget(new_price_label)
    price_box.addWidget(discount_label)
    card_layout.addLayout(price_box)
    
    card.setLayout(card_layout)
    
    # ДЗ: Подсветка, если остаток <= 3 + анимация наведения
    if product[4] <= 3:
        card.setStyleSheet("""
            #productCard { background-color: #ff8080; border: 1px solid #CCCCCC; border-radius: 8px; }
            #productCard:hover { background-color: #FFFFFF; border: 2px solid #2E8B57; }
        """)
    else:
        card.setStyleSheet("""
            #productCard { background-color: #F9F9F9; border: 1px solid #CCCCCC; border-radius: 8px; }
            #productCard:hover { background-color: #FFFFFF; border: 2px solid #2E8B57; }
        """)
    
    return card

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None, role_name=None, db=None): 
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name 
        self.role_name = role_name
        self.db = db if db else Database() 
        
        self.setWindowTitle("Мир здорового питания — Каталог")
        self.resize(850, 650)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setStyleSheet("QMainWindow { background-color: #FFFFFF; } QLabel { font-family: 'Calibri'; color: #000000; }")
        
        self.setup_ui()
        self.setup_role_interface()
        self.load_products() 

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        
        header = QHBoxLayout()
        logo_header = QLabel()
        if os.path.exists("resources/logo.png"):
            pixmap_logo = QPixmap("resources/logo.png")
            if not pixmap_logo.isNull():
                logo_header.setPixmap(pixmap_logo.scaledToHeight(40, Qt.TransformationMode.SmoothTransformation))
        header.addWidget(logo_header)
        header.addStretch()
        
        self.name_label = QLabel(f"ФИО: {self.full_name} ({self.role_name})")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header.addWidget(self.name_label)
        
        self.settings_button = QPushButton("Настройки")
        self.settings_button.setStyleSheet("background-color: #1976D2; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
        header.addWidget(self.settings_button)
        
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("background-color: #D32F2F; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold;")
        self.logout_button.clicked.connect(self.logout)
        header.addWidget(self.logout_button)
        main_layout.addLayout(header)

        # ДЗ: Заголовок и версия приложения
        title_label = QLabel("Мир здорового питания")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        version_label = QLabel("Версия приложения: v1.0")
        version_label.setStyleSheet("color: #888; font-size: 12px; margin-bottom: 10px;")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(version_label)
        
        buttons_layout = QHBoxLayout()
        self.order_button = QPushButton("Оформить заказ")
        self.order_button.setStyleSheet("background-color: #2E7D32; color: white; padding: 8px; border-radius: 4px;")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.setStyleSheet("background-color: #1976D2; color: white; padding: 8px; border-radius: 4px;")
        self.admin_button = QPushButton("Админ-панель")
        self.admin_button.setStyleSheet("background-color: #757575; color: white; padding: 8px; border-radius: 4px;")
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        main_layout.addLayout(buttons_layout)

        # ДЗ: Сортировка и Фильтр
        filters_layout = QHBoxLayout()
        
        self.filter_checkbox = QCheckBox("Только со скидкой > 15%")
        self.filter_checkbox.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.filter_checkbox.clicked.connect(self.load_products) 
        filters_layout.addWidget(self.filter_checkbox)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Сортировка: по скидке", "Цена (по возрастанию)", "Цена (по убыванию)"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        filters_layout.addWidget(self.sort_combo)
        
        main_layout.addLayout(filters_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)
        
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def load_products(self):
        self.scroll_area.setUpdatesEnabled(False)
        
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                
        conn = self.db.get_connection()
        if not conn: 
            self.scroll_area.setUpdatesEnabled(True)
            return
            
        cursor = conn.cursor()
        products = self.db.get_products()
        products_data = []
        
        for p in products:
            old_price = float(p[3])
            new_price, disc_size = calculate_price(p[0], old_price, cursor)
            disc_percent = calculate_discount(old_price, new_price)
            products_data.append((p, disc_percent, new_price))
            
        cursor.close()
        self.db.release_connection(conn)
        
        # ДЗ: Сортировка
        sort_idx = self.sort_combo.currentIndex()
        if sort_idx == 1:
            products_data.sort(key=lambda x: x[2]) # По цене возрастание
        elif sort_idx == 2:
            products_data.sort(key=lambda x: x[2], reverse=True) # По цене убывание
        else:
            products_data.sort(key=lambda x: x[1], reverse=True) # По скидке
            
        if self.filter_checkbox.isChecked():
            products_data = [item for item in products_data if item[1] > 15]
            
        for product, discount, new_price in products_data:
            card = create_card(product, discount, new_price)
            self.scroll_layout.addWidget(card)
            
        self.scroll_area.setUpdatesEnabled(True)

    def setup_role_interface(self):
        for btn in [self.order_button, self.manager_button, self.admin_button, self.settings_button]:
            btn.hide()
            btn.setEnabled(False)
        
        if self.role_id == 1:
            self.admin_button.show()
            self.admin_button.setEnabled(True)
            self.manager_button.show()
            self.manager_button.setEnabled(True)
            self.settings_button.show() 
            self.settings_button.setEnabled(True)
        elif self.role_id == 2:
            self.manager_button.show()
            self.manager_button.setEnabled(True)
        elif self.role_id == 3:
            self.order_button.show()
            self.order_button.setEnabled(True)

    def logout(self):
        from login_window import LoginWindow
        self.login_window = LoginWindow(self.db)
        self.login_window.show()
        self.close()

    def closeEvent(self, event):
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    from login_window import LoginWindow
    login_window = LoginWindow(db)
    login_window.show()
    exit_code = app.exec()
    db.close_all()
    sys.exit(exit_code)