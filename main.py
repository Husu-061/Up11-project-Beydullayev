import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                               QWidget, QHBoxLayout, QScrollArea, QPushButton)  
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database


def create_card(product):
    card = QWidget()
    card_layout = QHBoxLayout()
    card_layout.setContentsMargins(10, 10, 10, 10)
    
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
    else:
        img_label.setText("Нет фото")
        
    card_layout.addWidget(img_label)
    
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
    
    price_label = QLabel(f"{product[3]} руб.")
    price_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2E7D32; border: none;")
    price_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    card_layout.addWidget(price_label)
    
    card.setLayout(card_layout)
    card.setStyleSheet("background-color: #F9F9F9; border: 1px solid #CCCCCC; border-radius: 8px;")
    return card


class MainWindow(QMainWindow):
    def __init__(self, role_id=None):
        super().__init__()
        self.role_id = role_id 
        
        self.setWindowTitle("Мир здорового питания — Каталог")
        self.resize(800, 600)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.db = Database()
        self.setStyleSheet("QMainWindow { background-color: #FFFFFF; } QLabel { font-family: 'Calibri'; color: #000000; }")
        
        # Вызываем методы настройки (они должны быть внутри класса с отступом!)
        self.setup_ui()
        self.setup_role_interface()

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        
        # Заголовок и Логотип
        title_label = QLabel("Мир здорового питания")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap_logo = QPixmap("resources/logo.png")
        if not pixmap_logo.isNull():
            logo.setPixmap(pixmap_logo.scaledToHeight(80, Qt.TransformationMode.SmoothTransformation))
        main_layout.addWidget(logo)

        # Создаем кнопки
        buttons_layout = QHBoxLayout()
        
        self.order_button = QPushButton("Оформить заказ")
        self.order_button.setStyleSheet("background-color: #2E7D32; color: white; padding: 8px; border-radius: 4px;")
        
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.setStyleSheet("background-color: #1976D2; color: white; padding: 8px; border-radius: 4px;")
        
        self.admin_button = QPushButton("Админ-панель")
        self.admin_button.setStyleSheet("background-color: #D32F2F; color: white; padding: 8px; border-radius: 4px;")
        
        buttons_layout.addWidget(self.order_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        main_layout.addLayout(buttons_layout)

        # Каталог с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        
        self.products = self.db.get_products()
        for product in self.products:
            card = create_card(product)
            scroll_layout.addWidget(card)
            
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def setup_role_interface(self):
        # Сначала скрываем все
        self.order_button.hide()
        self.manager_button.hide()
        self.admin_button.hide()
        
        # Показываем по ролям
        if self.role_id == 1:
            self.admin_button.show()
            self.manager_button.show()
        elif self.role_id == 2:
            self.manager_button.show()
        elif self.role_id == 3:
            self.order_button.show()

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