from PySide6.QtWidgets import (QDialog, QLineEdit, QPushButton, 
                               QVBoxLayout, QLabel, QMessageBox)
from PySide6.QtGui import QIcon
import sys

class LoginWindow(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        self.full_name = None
        
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Введите логин")
        layout.addWidget(self.login_input)
        
        self.login_button = QPushButton("Войти")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)

    def check_login(self):
        login = self.login_input.text().strip()
        
        # ЗАДАНИЕ 1.1: Error для пустого логина
        if not login:
            QMessageBox.critical(self, "Ошибка", "Введите логин")
            return
            
        query = """
            SELECT u.user_id, u.role_id, u.last_name, u.first_name, u.middle_name, r.name 
            FROM users u 
            JOIN roles r ON u.role_id = r.role_id 
            WHERE u.login = %s
        """
        result = self.db.execute_query(query, (login,))
        
        if result:
            user_data = result[0]
            self.user_id = user_data[0]
            self.role_id = user_data[1]
            
            last_name, first_name, middle_name = user_data[2], user_data[3], user_data[4]
            role_name = user_data[5]
            
            if middle_name:
                self.full_name = f"{last_name} {first_name} {middle_name}"
            else:
                self.full_name = f"{last_name} {first_name}"
            
            # ЗАДАНИЕ 3.1: Information для успешного входа
            QMessageBox.information(self, "Информация", f"Добро пожаловать, {self.full_name}!")
            
            self.accept()
            
            from main import MainWindow
            self.main_window = MainWindow(
                user_id=self.user_id, 
                role_id=self.role_id, 
                full_name=self.full_name, 
                role_name=role_name, 
                db=self.db
            )
            self.main_window.show()
        else:
            # ЗАДАНИЕ 1.2: Error для неверного логина
            QMessageBox.critical(self, "Ошибка", "Пользователь не найден")