from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QMessageBox)

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
            QMessageBox.warning(self, "Ошибка", "Введите логин!")
            return
            
        conn = self.db.get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Нет подключения к базе данных!")
            return
            
        try:
            cur = conn.cursor()
            # ДЗ: Добавили JOIN с таблицей roles, чтобы получить название роли
            query = """
                SELECT u.user_id, u.role_id, u.last_name, u.first_name, u.middle_name, r.name 
                FROM users u 
                JOIN roles r ON u.role_id = r.role_id 
                WHERE u.login = %s
            """
            cur.execute(query, (login,))
            result = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка: {e}")
            result = None
        finally:
            self.db.release_connection(conn)
            
        if result is None:
            QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")
        else:
            self.user_id = result[0]
            self.role_id = result[1]
            
            last_name, first_name, middle_name = result[2], result[3], result[4]
            role_name = result[5] # Название роли из БД
            
            if middle_name:
                self.full_name = f"{last_name} {first_name} {middle_name}"
            else:
                self.full_name = f"{last_name} {first_name}"
            
            from main import MainWindow
            # Передаем role_name в MainWindow
            self.main_window = MainWindow(role_id=self.role_id, full_name=self.full_name, role_name=role_name)
            self.main_window.show()
            self.close()