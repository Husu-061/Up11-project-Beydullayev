from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton)

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        self.full_name = None
        
        self.setWindowTitle("Авторизация")
        self.resize(300, 200)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Логин:"))
        self.login_input = QLineEdit()
        layout.addWidget(self.login_input)
        
        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.check_login)
        layout.addWidget(self.btn_login)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget { background-color: #FFFFFF; font-family: 'Calibri'; font-size: 14px; }
            QLineEdit { padding: 5px; border: 1px solid #CCC; border-radius: 4px; }
            QPushButton { background-color: #2E7D32; color: white; padding: 8px; border-radius: 4px; font-weight: bold; }
        """)

    def check_login(self):
        login = self.login_input.text().strip()
        
        if not login:
            print("Ошибка: Введите логин!")
            return
            
        query = """
            SELECT u.user_id, u.role_id, u.last_name, u.first_name, u.middle_name, r.name 
            FROM users u 
            JOIN roles r ON u.role_id = r.role_id 
            WHERE u.login = %s
        """
        result = self.db.execute_query(query, (login,))
        
        if not result:
            print("Ошибка: Пользователь не найден!")
        else:
            user_data = result[0]
            self.user_id = user_data[0]
            self.role_id = user_data[1]
            
            last_name, first_name, middle_name = user_data[2], user_data[3], user_data[4]
            role_name = user_data[5]
            
            if middle_name:
                self.full_name = f"{last_name} {first_name} {middle_name}"
            else:
                self.full_name = f"{last_name} {first_name}"
            
            from main import MainWindow
            self.main_window = MainWindow(role_id=self.role_id, full_name=self.full_name, role_name=role_name, db=self.db)
            self.main_window.show()
            self.close()