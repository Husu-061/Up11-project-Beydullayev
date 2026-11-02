import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                               QWidget, QHBoxLayout, QScrollArea, QPushButton) 
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from database import Database

# ==========================================
# Функция создания карточки товара
# ==========================================
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

# ==========================================
# Главное окно (с ФИО, выходом и ролями)
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self, role_id=None, user_name="Гость"):
        super().__init__()
        self.role_id = role_id
        self.user_name = user_name
        
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
        

        top_layout = QHBoxLayout()
        
        self.user_label = QLabel(f"Вы вошли как: {self.user_name}")
        self.user_label.setStyleSheet("font-weight: bold; color: #555; font-size: 14px;")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        self.logout_button = QPushButton("Выход")
        self.logout_button.setStyleSheet("background-color: #D32F2F; color: white; padding: 5px 15px; border-radius: 4px; font-weight: bold;")
        self.logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_button.clicked.connect(self.logout)
        
        top_layout.addWidget(self.user_label)
        top_layout.addWidget(self.logout_button)
        main_layout.addLayout(top_layout)
 
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

        # Кнопки ролей
        buttons_layout = QHBoxLayout()
        
        self.order_button = QPushButton("Оформить заказ")
        self.order_button.setStyleSheet("background-color: #2E7D32; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.setStyleSheet("background-color: #1976D2; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        
        self.admin_button = QPushButton("Админ-панель")
        self.admin_button.setStyleSheet("background-color: #757575; color: white; padding: 8px; border-radius: 4px; font-weight: bold;")
        
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
        for btn in [self.order_button, self.manager_button, self.admin_button]:
            btn.hide()
            btn.setEnabled(False)
        
        # Показываем и разблокируем нужные
        if self.role_id == 1: # Администратор
            self.admin_button.show()
            self.admin_button.setEnabled(True)
            self.manager_button.show()
            self.manager_button.setEnabled(True)
        elif self.role_id == 2: # Менеджер
            self.manager_button.show()
            self.manager_button.setEnabled(True)
        elif self.role_id == 3: # Клиент
            self.order_button.show()
            self.order_button.setEnabled(True)

    def logout(self):
        # Возврат к окну авторизации
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