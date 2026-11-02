from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QMessageBox)

class LoginWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.user_id = None
        self.role_id = None
        
        # Задание 2: Интерфейс
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
            QPushButton:hover { background-color: #1B5E20; }
        """)

    def check_login(self):
        # Задание 3: Проверка логина
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
            query = "SELECT user_id, role_id FROM users WHERE login = %s"
            cur.execute(query, (login,))
            result = cur.fetchone()
            cur.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка БД", f"Ошибка выполнения запроса: {e}")
            result = None
        finally:
            self.db.release_connection(conn)
            
        if result is None:
            QMessageBox.warning(self, "Ошибка", "Пользователь с таким логином не найден!")
        else:
            self.user_id = result[0]
            self.role_id = result[1]
            
            # ==========================================
            # ЗАДАНИЕ 4: Переход к главному окну
            # ==========================================
            from main import MainWindow
            
            # Создаем и показываем главное окно, передавая ему role_id
            self.main_window = MainWindow(role_id=self.role_id)
            self.main_window.show()
            
            # Закрываем окно входа
            self.close()