import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                               QWidget, QHBoxLayout, QScrollArea, QPushButton, 
                               QMessageBox, QStyle, QCheckBox) 
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database


def calculate_discount(old_price, new_price):
    if old_price == 0:
        return 0
    return (old_price - new_price) / old_price * 100


def calculate_price(product_id, old_price, cursor):
    query = """
        SELECT COUNT(*) 
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE oi.product_id = %s 
        AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
    """
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()
    orders_count = result[0] if result else 0
    
    if orders_count == 0:
        return float(old_price) * 0.75 
    return float(old_price)


def create_card(product, discount): 
    card = QWidget()
    card_layout = QHBoxLayout()
    card_layout.setContentsMargins(10, 10, 10, 10)
    
    # Изображение
    img_label = QLabel()
    img_label.setFixedSize(100, 100)
    img_label.setStyleSheet("border: 1px solid #ddd; background-color: #fff;")
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    image_path = product[5]
    pixmap = QPixmap()
    if image_path is not None and os.path.exists(f"Images/{image_path}"):
        pixmap = QPixmap(f"Images/{image_path}")
    else:
        pixmap = QPixmap("resources/picture.png")
        
    if not pixmap.isNull():
        img_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    card_layout.addWidget(img_label)
    
    # Текст
    text_layout = QVBoxLayout()
    name_label = QLabel(f"Наименование: {product[2]}")
    name_label.setStyleSheet("font-weight: bold; font-size: 16px; border: none;")
    category_label = QLabel(f"Категория: {product[1]}")
    category_label.setStyleSheet("border: none;")
    stock_label = QLabel(f"В наличии: {product[4]} шт.")
    stock_label.setStyleSheet("border: none;")
    
    text_layout.addWidget(name_label)
    text_layout.addWidget(category_label)
    text_layout.addWidget(stock_label)
    card_layout.addLayout(text_layout)
    
    # Цена и Скидка
    old_price = float(product[3])
    new_price = old_price * (1 - discount / 100) if discount > 0 else old_price
    
    price_box = QVBoxLayout()
    price_box.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    
    price_label = QLabel(f"{new_price:.2f} руб.")
    discount_label = QLabel(f"-{int(discount)}%")
    discount_label.setAlignment(Qt.AlignmentFlag.AlignRight)
    
    # ДЗ: Разные цвета для разных скидок
    if discount > 30:
        price_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #E65100; border: none;")
        discount_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #E65100; border: none;")
    elif discount > 15:
        price_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2E8B57; border: none;")
        discount_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2E8B57; border: none;")
    else:
        price_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2E7D32; border: none;")
        discount_label.hide() 
        
    price_box.addWidget(price_label)
    price_box.addWidget(discount_label)
    card_layout.addLayout(price_box)
    
    card.setLayout(card_layout)
    card.setStyleSheet("background-color: #F9F9F9; border: 1px solid #CCCCCC; border-radius: 8px;")
    return card


class MainWindow(QMainWindow):
    def __init__(self, role_id=None, full_name=None, role_name=None): 
        super().__init__()
        self.role_id = role_id
        self.full_name = full_name 
        self.role_name = role_name
        
        self.setWindowTitle("Мир здорового питания — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.db = Database()
        self.setStyleSheet("QMainWindow { background-color: #FFFFFF; } QLabel { font-family: 'Calibri'; color: #000000; }")
        
        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        
        # Шапка (Header)
        header = QHBoxLayout()
        logo_header = QLabel()
        pixmap_logo = QPixmap("resources/logo.png")
        if not pixmap_logo.isNull():
            logo_header.setPixmap(pixmap_logo.scaledToHeight(40, Qt.TransformationMode.SmoothTransformation))
        header.addWidget(logo_header)
        header.addStretch()
        
        user_icon = QLabel()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogInfoView)
        user_icon.setPixmap(icon.pixmap(24, 24))
        header.addWidget(user_icon)
        
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

        title_label = QLabel("Мир здорового питания")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Кнопки ролей
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

        # ДЗ: Фильтр
        self.filter_checkbox = QCheckBox("Показывать только товары со скидкой > 15%")
        self.filter_checkbox.setStyleSheet("font-size: 14px; margin: 10px; font-weight: bold;")
        self.filter_checkbox.stateChanged.connect(self.load_products)
        main_layout.addWidget(self.filter_checkbox)

        # Каталог (QScrollArea)
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
        
        # Загружаем товары при старте
        self.load_products()

    # ДЗ: Метод загрузки, сортировки и фильтрации
    def load_products(self):
        # Очищаем список (безопасно, без ошибок None)
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                
        conn = self.db.get_connection()
        if not conn:
            return
        cursor = conn.cursor()
        
        self.products = self.db.get_products()
        products_data = []
        
        for p in self.products:
            old_price = float(p[3])
            new_price = calculate_price(p[0], old_price, cursor)
            disc = calculate_discount(old_price, new_price)
            products_data.append((p, disc))
            
        cursor.close()
        self.db.release_connection(conn)
        
        # ДЗ: Сортировка по размеру скидки
        products_data.sort(key=lambda x: x[1], reverse=True)
        
        # ДЗ: Фильтрация
        if self.filter_checkbox.isChecked():
            products_data = [item for item in products_data if item[1] > 15]
            
        # Отрисовка карточек
        for product, discount in products_data:
            card = create_card(product, discount)
            self.scroll_layout.addWidget(card)

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
        reply = QMessageBox.question(self, 'Выход', 'Вы уверены, что хотите выйти?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        self.db.close_all()
        event.accept()

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from database import Database
    from login_window import LoginWindow  
    
    app = QApplication(sys.argv)
    db = Database()
    login_window = LoginWindow(db)
    login_window.show()
    sys.exit(app.exec())