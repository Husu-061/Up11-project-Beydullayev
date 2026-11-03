import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                               QWidget, QHBoxLayout, QScrollArea, QPushButton, 
                               QCheckBox, QComboBox, QLineEdit) 
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database

image_cache = {}

def calculate_discount(old_price, new_price):
    if old_price == 0: return 0
    return (old_price - new_price) / old_price * 100

def calculate_price(product_id, old_price, cursor):
    try:
        cursor.execute("SELECT name FROM products WHERE product_id = %s", (product_id,))
        name_res = cursor.fetchone()
        
        query = """
            SELECT COUNT(*) FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        orders_count = result[0] if result else 0
        
        final_price = float(old_price) * 0.75 if orders_count == 0 else float(old_price)
        return final_price, float(old_price) - final_price
    except Exception:
        return float(old_price), 0.0

def create_card(product, discount, new_price): 
    card = QWidget()
    card.setObjectName("productCard")
    card_layout = QHBoxLayout()
    card_layout.setContentsMargins(10, 10, 10, 10)
    
    image_path = product[4] 
    total_quantity = product[5] 
    
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
    name_label.setStyleSheet("color: black; font-weight: bold; font-size: 16px; border: none; background: transparent;")
    category_label = QLabel(f"Категория: {product[1]}")
    category_label.setStyleSheet("color: black; border: none; background: transparent;")
    
    stock_label = QLabel()
    if total_quantity == 0:
        stock_label.setText("Нет в наличии")
        stock_label.setStyleSheet("color: red; font-weight: bold; border: none; background: transparent;")
    else:
        stock_label.setText(f"В наличии: {total_quantity} шт.")
        stock_label.setStyleSheet("color: black; border: none; background: transparent;")
    
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
    
    order_btn = QPushButton("Оформить заказ")
    if total_quantity == 0:
        order_btn.setEnabled(False)
        order_btn.setText("Нет в наличии")
        order_btn.setStyleSheet("QPushButton { background-color: #999999; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; margin-top: 5px; font-family: Calibri; }")
    else:
        order_btn.setStyleSheet("QPushButton { background-color: #70B2AF; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; margin-top: 5px; font-family: Calibri; }")
        
    price_box.addWidget(order_btn)
    card_layout.addLayout(price_box)
    card.setLayout(card_layout)
    
    if total_quantity == 0:
        card.setStyleSheet("#productCard { background-color: #ADD8E6; border: 1px solid #999999; border-radius: 8px; }")
    else:
        card.setStyleSheet("#productCard { background-color: #F9F9F9; border: 1px solid #CCCCCC; border-radius: 8px; } #productCard:hover { background-color: #FFFFFF; border: 2px solid #70B2AF; }")
    
    return card

class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None, role_name=None, db=None): 
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name 
        self.role_name = role_name
        self.db = db if db else Database() 
        
        self.setWindowTitle("Мир здорового питания — Каталог")
        self.resize(950, 700) # Сделали окно чуть шире для новых фильтров
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setup_ui()
        self.setup_role_interface()
        self.load_products() 

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        
        header_layout = QHBoxLayout()
        logo_header = QLabel()
        if os.path.exists("resources/logo.png"):
            pixmap_logo = QPixmap("resources/logo.png")
            if not pixmap_logo.isNull():
                logo_header.setPixmap(pixmap_logo.scaledToHeight(40, Qt.TransformationMode.SmoothTransformation))
        header_layout.addWidget(logo_header)
        header_layout.addStretch()
        
        self.name_label = QLabel(f"ФИО: {self.full_name} ({self.role_name})")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.name_label)
        
        self.theme_button = QPushButton("Тёмная тема")
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)
        
        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)
        
        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)

        title_label = QLabel("Мир здорового питания")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)

        buttons_layout = QHBoxLayout()
        self.order_button = QPushButton("Оформить заказ")
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.admin_button = QPushButton("Админ-панель")
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        main_layout.addLayout(buttons_layout)

        # ==========================================
        # ДЗ: Панель поиска, фильтра, сортировки и сброса
        # ==========================================
        filters_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        filters_layout.addWidget(self.search_input)
        
        # Фильтр по категории
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        categories = self.db.get_categories()
        self.filter_combo.addItems(categories)
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        filters_layout.addWidget(self.filter_combo)
        
        # ДЗ: Фильтр по производителю
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItem("Все производители")
        manufacturers = self.db.get_manufacturers()
        self.manufacturer_combo.addItems(manufacturers)
        self.manufacturer_combo.currentIndexChanged.connect(self.load_products)
        filters_layout.addWidget(self.manufacturer_combo)
        
        # ДЗ: Сортировка (добавили "По наименованию")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "По возрастанию цены", 
            "По убыванию цены", 
            "По наименованию (А-Я)", 
            "По скидке", 
            "Сначала в наличии"
        ])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        filters_layout.addWidget(self.sort_combo)
        
        # ДЗ (Доп): Кнопка сброса
        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.reset_filters)
        filters_layout.addWidget(self.reset_button)
        
        main_layout.addLayout(filters_layout)

        # Чекбоксы
        checkboxes_layout = QHBoxLayout()
        self.filter_checkbox = QCheckBox("Только со скидкой > 15%")
        self.filter_checkbox.clicked.connect(self.load_products) 
        checkboxes_layout.addWidget(self.filter_checkbox)

        self.in_stock_checkbox = QCheckBox("Только в наличии")
        self.in_stock_checkbox.clicked.connect(self.load_products)
        checkboxes_layout.addWidget(self.in_stock_checkbox)
        main_layout.addLayout(checkboxes_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)
        
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def toggle_theme(self):
        app = QApplication.instance()
        if isinstance(app, QApplication):
            if self.theme_button.text() == "Тёмная тема":
                with open("style_dark.qss", "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
                self.theme_button.setText("Светлая тема")
            else:
                with open("style_light.qss", "r", encoding="utf-8") as f:
                    app.setStyleSheet(f.read())
                self.theme_button.setText("Тёмная тема")

    # ДЗ (Доп): Метод сброса всех фильтров
    def reset_filters(self):
        # Блокируем сигналы, чтобы не было 5 перерисовок подряд
        self.search_input.blockSignals(True)
        self.filter_combo.blockSignals(True)
        self.manufacturer_combo.blockSignals(True)
        self.sort_combo.blockSignals(True)
        self.filter_checkbox.blockSignals(True)
        self.in_stock_checkbox.blockSignals(True)

        self.search_input.clear()
        self.filter_combo.setCurrentIndex(0)
        self.manufacturer_combo.setCurrentIndex(0)
        self.sort_combo.setCurrentIndex(0)
        self.filter_checkbox.setChecked(False)
        self.in_stock_checkbox.setChecked(False)

        # Включаем сигналы обратно
        self.search_input.blockSignals(False)
        self.filter_combo.blockSignals(False)
        self.manufacturer_combo.blockSignals(False)
        self.sort_combo.blockSignals(False)
        self.filter_checkbox.blockSignals(False)
        self.in_stock_checkbox.blockSignals(False)

        # Перерисовываем каталог
        self.load_products()

    def load_products(self):
        self.scroll_area.setUpdatesEnabled(False)
        
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                
        search_text = f"%{self.search_input.text()}%"
        category = self.filter_combo.currentText()
        manufacturer = self.manufacturer_combo.currentText() # ДЗ
        sort_by = self.sort_combo.currentText()
        
        # Обновленный SQL-запрос с учетом производителя
        query = """
            SELECT p.product_id, c.name, p.name, p.price, p.image_path,
                   COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            WHERE p.name ILIKE %s
            AND (c.name = %s OR %s = 'Все категории')
            AND (p.manufacturer = %s OR %s = 'Все производители')
            GROUP BY p.product_id, c.name, p.name, p.price, p.image_path
        """
        
        if sort_by == "По возрастанию цены":
            query += " ORDER BY p.price ASC"
        elif sort_by == "По убыванию цены":
            query += " ORDER BY p.price DESC"
        elif sort_by == "По наименованию (А-Я)":
            query += " ORDER BY p.name ASC"
        else:
            query += " ORDER BY p.product_id ASC"
            
        conn = self.db.get_connection()
        if not conn: 
            self.scroll_area.setUpdatesEnabled(True)
            return
            
        cursor = conn.cursor()
        # Передаем параметры (добавили manufacturer дважды)
        cursor.execute(query, (search_text, category, category, manufacturer, manufacturer))
        products = cursor.fetchall()
        
        products_data = []
        for p in products:
            old_price = float(p[3])
            new_price, disc_size = calculate_price(p[0], old_price, cursor)
            disc_percent = calculate_discount(old_price, new_price)
            products_data.append((p, disc_percent, new_price))
            
        cursor.close()
        self.db.release_connection(conn)
        
        if sort_by == "По скидке":
            products_data.sort(key=lambda x: x[1], reverse=True)
        elif sort_by == "Сначала в наличии":
            products_data.sort(key=lambda x: x[0][5] == 0)
            
        if self.filter_checkbox.isChecked():
            products_data = [item for item in products_data if item[1] > 15]
        if self.in_stock_checkbox.isChecked():
            products_data = [item for item in products_data if item[0][5] > 0]
            
        for product, discount, new_price in products_data:
            card = create_card(product, discount, new_price)
            self.scroll_layout.addWidget(card)
            
        self.scroll_area.setUpdatesEnabled(True)

    def setup_role_interface(self):
        for btn in [self.order_button, self.manager_button, self.admin_button]:
            btn.hide()
            btn.setEnabled(False)
        
        if self.role_id == 1:
            self.admin_button.show()
            self.admin_button.setEnabled(True)
            self.manager_button.show()
            self.manager_button.setEnabled(True)
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
    try:
        with open("style_light.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception:
        pass

    db = Database()
    from login_window import LoginWindow
    login_window = LoginWindow(db)
    login_window.show()
    exit_code = app.exec()
    db.close_all()
    sys.exit(exit_code)