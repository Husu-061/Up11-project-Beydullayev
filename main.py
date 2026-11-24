import os
import sys
import shutil
import uuid
from PySide6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, 
                               QWidget, QHBoxLayout, QScrollArea, QPushButton, 
                               QCheckBox, QComboBox, QLineEdit, QStackedWidget, 
                               QSizePolicy, QTableWidget, QTableWidgetItem, 
                               QHeaderView, QMessageBox, QDialog, QSpinBox,
                               QFileDialog)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt, QStandardPaths
from database import Database

DISCOUNT_RATE = 0.75
IMAGE_CACHE = {}

def get_image_path(image_name):
    if not image_name:
        return "resources/picture.png"
    app_data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
    if app_data_dir:
        app_images_dir = os.path.join(app_data_dir, "images")
        full_path = os.path.join(app_images_dir, image_name)
        if os.path.exists(full_path):
            return full_path
    project_images_dir = "Images"
    full_path = os.path.join(project_images_dir, image_name)
    if os.path.exists(full_path):
        return full_path
    return "resources/picture.png"

def calculate_discount(old_price, new_price):
    if old_price == 0: 
        return 0
    return (old_price - new_price) / old_price * 100

def calculate_price(product_id, old_price, cursor):
    try:
        cursor.execute("SELECT name FROM products WHERE product_id = %s", (product_id,))
        query = """
            SELECT COUNT(*) FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.product_id = %s AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
        """
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        orders_count = result[0] if result else 0
        if orders_count == 0:
            final_price = float(old_price) * DISCOUNT_RATE
        else:
            final_price = float(old_price)
        discount_size = float(old_price) - final_price
        return final_price, discount_size
    except Exception:
        return float(old_price), 0.0

def create_card(product, discount, new_price, sizes, main_window): 
    card = QWidget()
    card.setObjectName("productCard")
    card_layout = QHBoxLayout()
    card_layout.setContentsMargins(10, 10, 10, 10)

    image_path = product[4]
    manufacturer = product[5]
    total_quantity = product[6]

    full_image_path = get_image_path(image_path)
    if image_path not in IMAGE_CACHE:
        pixmap = QPixmap(full_image_path)
        IMAGE_CACHE[image_path] = pixmap

    img_label = QLabel()
    img_label.setFixedSize(100, 100)
    img_label.setStyleSheet("border: 1px solid #ddd; background-color: #fff;")
    img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    pixmap = IMAGE_CACHE[image_path]
    if not pixmap.isNull():
        img_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
    card_layout.addWidget(img_label)

    text_layout = QVBoxLayout()
    name_label = QLabel(f"Наименование: {product[2]}")
    name_label.setStyleSheet("color: black; font-weight: bold; font-size: 16px; border: none; background: transparent;")
    manufacturer_label = QLabel(f"Производство: {manufacturer if manufacturer else 'Не указано'}")
    manufacturer_label.setStyleSheet("color: #555; border: none; background: transparent;")
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
    text_layout.addWidget(manufacturer_label)
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

    details_btn = QPushButton("Подробнее")
    details_btn.setStyleSheet("QPushButton { background-color: #70B2AF; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; margin-top: 5px; font-family: Calibri; }")
    details_btn.clicked.connect(lambda checked=False, pid=product[0]: main_window.open_product_card(pid))
    price_box.addWidget(details_btn)

    size_combo = QComboBox()
    size_combo.setStyleSheet("""
        QComboBox { background-color: #FFFFFF; color: #000000; padding: 5px; border: 1px solid #CCC; border-radius: 4px; font-family: Calibri; }
        QComboBox QAbstractItemView { background-color: #FFFFFF; color: #000000; selection-background-color: #70B2AF; selection-color: white; }
    """)
    for size_id, size_value in sizes:
        size_combo.addItem(str(size_value), size_id)
    price_box.addWidget(size_combo)

    order_btn = QPushButton("Оформить заказ")
    if total_quantity == 0:
        order_btn.setEnabled(False)
        order_btn.setText("Нет в наличии")
        order_btn.setStyleSheet("QPushButton { background-color: #999999; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; margin-top: 5px; font-family: Calibri; }")
    else:
        order_btn.setStyleSheet("QPushButton { background-color: #70B2AF; color: white; padding: 5px 10px; border-radius: 4px; font-weight: bold; margin-top: 5px; font-family: Calibri; }")
        order_btn.clicked.connect(lambda checked, pid=product[0], sc=size_combo: main_window.add_to_order(pid, sc.currentData()))

    price_box.addWidget(order_btn)
    card_layout.addLayout(price_box)
    card.setLayout(card_layout)

    if total_quantity <= 3:
        card.setStyleSheet("#productCard { background-color: #ff8080; border: 1px solid #CCCCCC; border-radius: 8px; }")
    else:
        card.setStyleSheet("#productCard { background-color: #F9F9F9; border: 1px solid #CCCCCC; border-radius: 8px; } #productCard:hover { background-color: #FFFFFF; border: 2px solid #70B2AF; }")

    return card


class ProductCard(QDialog):
    def __init__(self, product_id, parent=None, role_id=None):
        super().__init__(parent)
        self.product_id = product_id
        self.parent_window = parent
        self.role_id = role_id
        self.db = parent.db if parent else Database()
        self.current_price = 0.0  # <--- ДОБАВЛЕНО: сохраняем актуальную цену
        self.setWindowTitle("Карточка товара")
        self.resize(400, 650)
        self.setup_ui()
        self.load_product(product_id)

    def setup_ui(self):
        layout = QVBoxLayout()
        self.image_label = QLabel()
        self.image_label.setFixedSize(300, 300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid #ddd; background-color: #fff;")
        layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel("Загрузка...")
        self.name_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        self.price_label = QLabel("")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.price_label)

        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555; font-size: 14px;")
        layout.addWidget(self.description_label)

        self.stock_label = QLabel("")
        self.stock_label.setStyleSheet("color: black; font-size: 14px;")
        layout.addWidget(self.stock_label)

        layout.addWidget(QLabel("Выберите фасовку:"))
        self.size_combo = QComboBox()
        self.size_combo.setStyleSheet("""
            QComboBox { background-color: #FFFFFF; color: #000000; padding: 5px; border: 1px solid #CCC; border-radius: 4px; }
            QComboBox QAbstractItemView { background-color: #FFFFFF; color: #000000; selection-background-color: #70B2AF; selection-color: white; }
        """)
        sizes = self.db.execute_query("SELECT size_id, value FROM sizes ORDER BY size_id")
        if sizes:
            for s_id, s_val in sizes:
                self.size_combo.addItem(str(s_val), s_id)
        layout.addWidget(self.size_combo)

        layout.addWidget(QLabel("Количество:"))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10)
        self.quantity_spin.setStyleSheet("padding: 5px; border: 1px solid #CCC; border-radius: 4px;")
        layout.addWidget(self.quantity_spin)

        if self.role_id == 1:
            self.load_image_button = QPushButton("Загрузить изображение")
            self.load_image_button.setStyleSheet("QPushButton { background-color: #1976D2; color: white; padding: 8px; border-radius: 5px; font-weight: bold; margin-top: 5px; }")
            self.load_image_button.clicked.connect(self.load_image)
            layout.addWidget(self.load_image_button)

        self.add_button = QPushButton("Добавить в корзину")
        self.add_button.setStyleSheet("QPushButton { background-color: #70B2AF; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 16px; margin-top: 10px; }")
        self.add_button.clicked.connect(self.add_selected_to_cart)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def load_product(self, product_id):
        query = """
            SELECT p.name, p.price, p.description, p.image_path,
                   COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            WHERE p.product_id = %s
            GROUP BY p.product_id, p.name, p.price, p.description, p.image_path
        """
        result = self.db.execute_query(query, (product_id,))
        if not result:
            QMessageBox.critical(self, "Ошибка", "Товар не найден")
            return
        name, old_price, description, image_path, total_quantity = result[0]
        conn = self.db.get_connection()
        orders_count = 0
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM order_items oi
                    JOIN orders o ON oi.order_id = o.order_id
                    WHERE oi.product_id = %s AND o.order_date >= CURRENT_DATE - INTERVAL '1 month'
                """, (product_id,))
                res = cursor.fetchone()
                orders_count = res[0] if res else 0
                cursor.close()
            except Exception as e:
                print(f"Ошибка скидки: {e}")
            finally:
                self.db.release_connection(conn)
        old_price_float = float(old_price)
        if orders_count == 0:
            new_price = old_price_float * DISCOUNT_RATE
            discount_percent = 25
        else:
            new_price = old_price_float
            discount_percent = 0

        # СОХРАНЯЕМ ЦЕНУ ДЛЯ КОРЗИНЫ
        self.current_price = new_price  

        self.name_label.setText(name)
        if discount_percent > 0:
            self.price_label.setText(
                f"<s style='color:red; font-size:16px;'>{old_price_float:.2f} ₽</s> "
                f"<span style='color:black; font-size:22px; font-weight:bold;'>{new_price:.2f} ₽</span> "
                f"<span style='color:#2E8B57;'>(скидка {discount_percent}%)</span>"
            )
        else:
            self.price_label.setText(f"Цена: {new_price:.2f} ₽")
        self.description_label.setText(description if description else "Описание отсутствует")
        self.stock_label.setText(f"В наличии: {total_quantity} шт.")
        full_image_path = get_image_path(image_path)
        pixmap = QPixmap(full_image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.image_label.setText("Нет изображения")
        self.quantity_spin.setMaximum(max(1, int(total_quantity)))
        if total_quantity == 0:
            self.add_button.setEnabled(False)
            self.add_button.setText("Нет в наличии")
            self.add_button.setStyleSheet("QPushButton { background-color: #999999; color: white; padding: 10px; border-radius: 5px; font-weight: bold; font-size: 16px; margin-top: 10px; }")

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите изображение", "", "Images (*.png *.jpg *.jpeg)")
        if not file_path:
            return
        test_pixmap = QPixmap(file_path)
        if test_pixmap.isNull():
            QMessageBox.warning(self, "Ошибка", "Выбранный файл не является изображением или повреждён.")
            return
        app_data_dir = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation)
        if not app_data_dir:
            app_data_dir = os.getcwd()
        images_dir = os.path.join(app_data_dir, "images")
        if not os.path.exists(images_dir):
            os.makedirs(images_dir, exist_ok=True)
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ('.png', '.jpg', '.jpeg'):
            QMessageBox.warning(self, "Ошибка", "Неподдерживаемый формат файла.")
            return
        new_filename = f"{uuid.uuid4().hex}{ext}"
        new_full_path = os.path.join(images_dir, new_filename)
        try:
            shutil.copy2(file_path, new_full_path)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось скопировать файл: {e}")
            return
        conn = self.db.get_connection()
        if not conn:
            os.remove(new_full_path)
            QMessageBox.critical(self, "Ошибка", "Нет подключения к БД")
            return
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET image_path = %s WHERE product_id = %s", (new_filename, self.product_id))
            conn.commit()
            cursor.close()
        except Exception as e:
            conn.rollback()
            os.remove(new_full_path)
            QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении БД: {e}")
            return
        finally:
            self.db.release_connection(conn)
        pixmap = QPixmap(new_full_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaled(300, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.image_label.setText("Не удалось загрузить изображение")
        if self.parent_window:
            self.parent_window.load_products()
        QMessageBox.information(self, "Успех", "Изображение успешно загружено.")

    def add_selected_to_cart(self):
        size_id = self.size_combo.currentData()
        qty = self.quantity_spin.value()
        name = self.name_label.text()
        
        # ИСПОЛЬЗУЕМ ЦЕНУ СО СКИДКОЙ
        price = self.current_price  
        
        if self.parent_window:
            self.parent_window.add_to_cart(name, qty, price, self.product_id, size_id)
            QMessageBox.information(self, "Успех", f"Товар '{name}' добавлен в корзину")
            self.accept()


class MainWindow(QMainWindow):
    def __init__(self, user_id=None, role_id=None, full_name=None, role_name=None, db=None): 
        super().__init__()
        self.user_id = user_id
        self.role_id = role_id
        self.full_name = full_name
        self.role_name = role_name
        self.db = db if db else Database()
        self.history = []
        self.setWindowTitle("Мир здорового питания — Каталог")
        self.resize(950, 700)
        self.setWindowIcon(QIcon("resources/icon.ico"))
        self.setup_ui()
        self.setup_role_interface()
        self.load_products()

    def setup_ui(self):
        central = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 10, 10, 10)
        logo_header = QLabel()
        if os.path.exists("resources/logo.png"):
            pixmap_logo = QPixmap("resources/logo.png")
            if not pixmap_logo.isNull():
                logo_header.setPixmap(pixmap_logo.scaledToHeight(40, Qt.TransformationMode.SmoothTransformation))
        header_layout.addWidget(logo_header)
        header_layout.addStretch()

        self.name_label = QLabel(f"ФИО: {self.full_name} ({self.role_name})")
        self.name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: black;")
        header_layout.addWidget(self.name_label)

        self.back_button = QPushButton("Назад")
        self.back_button.clicked.connect(self.go_back)
        self.back_button.setVisible(False) 
        header_layout.addWidget(self.back_button)

        self.theme_button = QPushButton("Тёмная тема")
        self.theme_button.clicked.connect(self.toggle_theme)
        header_layout.addWidget(self.theme_button)

        self.logout_button = QPushButton("Выход")
        self.logout_button.clicked.connect(self.logout)
        header_layout.addWidget(self.logout_button)

        header_widget = QWidget()
        header_widget.setObjectName("headerWidget")
        header_widget.setLayout(header_layout)
        header_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        header_widget.setFixedHeight(70)
        main_layout.addWidget(header_widget)

        self.stacked_widget = QStackedWidget()

        # Страница 0: Каталог
        self.catalog_page = QWidget()
        catalog_layout = QVBoxLayout()
        title_label = QLabel("Мир здорового питания")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px; color: black;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        catalog_layout.addWidget(title_label)

        buttons_layout = QHBoxLayout()
        self.my_orders_button = QPushButton("Мои заказы")
        self.my_orders_button.clicked.connect(lambda: self.switch_page(2))
        self.manager_button = QPushButton("Заказы (менеджер)")
        self.manager_button.clicked.connect(lambda: self.switch_page(2)) 
        self.admin_button = QPushButton("Админ-панель")
        self.cart_button = QPushButton("Корзина")
        self.cart_button.clicked.connect(lambda: self.switch_page(1))

        buttons_layout.addWidget(self.my_orders_button)
        buttons_layout.addWidget(self.manager_button)
        buttons_layout.addWidget(self.admin_button)
        buttons_layout.addWidget(self.cart_button)
        catalog_layout.addLayout(buttons_layout)

        filters_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.load_products)
        filters_layout.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Все категории")
        categories = self.db.get_categories()
        self.filter_combo.addItems(categories)
        self.filter_combo.currentIndexChanged.connect(self.load_products)
        filters_layout.addWidget(self.filter_combo)

        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItem("Все производители")
        manufacturers = self.db.get_manufacturers()
        self.manufacturer_combo.addItems(manufacturers)
        self.manufacturer_combo.currentIndexChanged.connect(self.load_products)
        filters_layout.addWidget(self.manufacturer_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["По возрастанию цены", "По убыванию цены", "По наименованию (А-Я)", "По скидке", "Сначала в наличии"])
        self.sort_combo.currentIndexChanged.connect(self.load_products)
        filters_layout.addWidget(self.sort_combo)

        self.reset_button = QPushButton("Сбросить")
        self.reset_button.clicked.connect(self.reset_filters)
        filters_layout.addWidget(self.reset_button)
        catalog_layout.addLayout(filters_layout)

        checkboxes_layout = QHBoxLayout()
        self.filter_checkbox = QCheckBox("Только со скидкой > 15%")
        self.filter_checkbox.clicked.connect(self.load_products)
        checkboxes_layout.addWidget(self.filter_checkbox)

        self.in_stock_checkbox = QCheckBox("Только в наличии")
        self.in_stock_checkbox.clicked.connect(self.load_products)
        checkboxes_layout.addWidget(self.in_stock_checkbox)
        catalog_layout.addLayout(checkboxes_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_widget)
        catalog_layout.addWidget(self.scroll_area)

        self.catalog_page.setLayout(catalog_layout)
        self.stacked_widget.addWidget(self.catalog_page)

        # Страница 1: Корзина
        self.cart_page = QWidget()
        cart_layout = QVBoxLayout()
        title_cart = QLabel("Корзина")
        title_cart.setStyleSheet("font-size: 24px; font-weight: bold; color: black; margin: 10px;")
        title_cart.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cart_layout.addWidget(title_cart)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["Наименование", "Количество", "Цена", "Сумма", "ID"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.cart_table.setColumnHidden(4, True)
        self.cart_table.itemSelectionChanged.connect(self.update_total)
        cart_layout.addWidget(self.cart_table)

        self.total_label = QLabel("Итого: 0 ₽")
        self.total_label.setStyleSheet("font-size: 20px; font-weight: bold; color: black; margin: 10px;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        cart_layout.addWidget(self.total_label)

        cart_buttons_layout = QHBoxLayout()
        self.remove_from_cart_btn = QPushButton("Удалить выбранное")
        self.remove_from_cart_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 8px; border-radius: 5px;")
        self.remove_from_cart_btn.clicked.connect(self.remove_from_cart)
        cart_buttons_layout.addWidget(self.remove_from_cart_btn)

        self.checkout_btn = QPushButton("Оформить заказ из корзины")
        self.checkout_btn.setStyleSheet("background-color: #70B2AF; color: white; padding: 8px; border-radius: 5px;")
        self.checkout_btn.clicked.connect(self.checkout_from_cart)
        cart_buttons_layout.addWidget(self.checkout_btn)
        cart_layout.addLayout(cart_buttons_layout)

        self.cart_page.setLayout(cart_layout)
        self.stacked_widget.addWidget(self.cart_page)

        # Страница 2: Заказы
        self.orders_page = QWidget()
        orders_layout = QVBoxLayout()
        title_orders = QLabel("Мои заказы")
        title_orders.setStyleSheet("font-size: 24px; font-weight: bold; color: black; margin: 10px;")
        title_orders.setAlignment(Qt.AlignmentFlag.AlignCenter)
        orders_layout.addWidget(title_orders)

        self.orders_table = QTableWidget()
        self.orders_table.setColumnCount(6)
        self.orders_table.setHorizontalHeaderLabels(["№ Заказа", "Дата", "Товар", "Кол-во", "Цена", "Действие"])
        self.orders_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.orders_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        orders_layout.addWidget(self.orders_table)

        self.orders_page.setLayout(orders_layout)
        self.stacked_widget.addWidget(self.orders_page)

        main_layout.addWidget(self.stacked_widget)
        central.setLayout(main_layout)
        self.setCentralWidget(central)

        self.stacked_widget.setCurrentIndex(0)
        self.update_title(0)

    def add_to_cart(self, name, quantity, price, product_id, size_id=None):
        row = self.cart_table.rowCount()
        self.cart_table.insertRow(row)
        self.cart_table.setItem(row, 0, QTableWidgetItem(name))
        self.cart_table.setItem(row, 1, QTableWidgetItem(str(quantity)))
        self.cart_table.setItem(row, 2, QTableWidgetItem(str(price)))
        self.cart_table.setItem(row, 3, QTableWidgetItem(str(quantity * price)))
        self.cart_table.setItem(row, 4, QTableWidgetItem(str(product_id)))
        self.update_total()

    def remove_from_cart(self):
        row = self.cart_table.currentRow()
        if row >= 0:
            self.cart_table.removeRow(row)
            self.update_total()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления")

    def update_total(self):
        total = 0.0
        for row in range(self.cart_table.rowCount()):
            item = self.cart_table.item(row, 3)
            if item and item.text():
                try:
                    total += float(item.text())
                except ValueError:
                    pass
        self.total_label.setText(f"Итого: {total:.2f} ₽")

    def checkout_from_cart(self):
        if self.cart_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста")
            return
        if not self.user_id:
            QMessageBox.warning(self, "Ошибка", "Пользователь не авторизован")
            return

        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (order_date, user_id) VALUES (CURRENT_DATE, %s) RETURNING order_id",
                (self.user_id,)
            )
            order_res = cursor.fetchone()
            if order_res is None:
                QMessageBox.critical(self, "Ошибка", "Не удалось создать заказ")
                return
            order_id = order_res[0]
            
            for row in range(self.cart_table.rowCount()):
                qty_item = self.cart_table.item(row, 1)
                price_item = self.cart_table.item(row, 2)
                pid_item = self.cart_table.item(row, 4)
                
                if qty_item is None or price_item is None or pid_item is None:
                    continue
                
                qty = int(qty_item.text())
                price = float(price_item.text())
                product_id = int(pid_item.text())
                
                cursor.execute("SELECT size_id FROM sizes LIMIT 1")
                size_res = cursor.fetchone()
                size_id = size_res[0] if size_res else 1
                
                cursor.execute(
                    "INSERT INTO order_items (order_id, product_id, size_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                    (order_id, product_id, size_id, qty, price)
                )
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", f"Заказ №{order_id} успешно оформлен!")
            self.cart_table.setRowCount(0)
            self.update_total()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при оформлении заказа: {e}")
        finally:
            self.db.release_connection(conn)

    def open_product_card(self, product_id):
        card = ProductCard(product_id, self, self.role_id)
        card.exec()
        self.load_products()

    def switch_page(self, index):
        if 0 <= index < self.stacked_widget.count():
            current = self.stacked_widget.currentIndex()
            if current != index:
                self.history.append(current)
            self.stacked_widget.setCurrentIndex(index)
            self.update_title(index)
            self.back_button.setVisible(index > 0)
            if index == 0:
                self.load_products()
            elif index == 1:
                self.update_total()
            elif index == 2:
                self.load_orders()

    def go_back(self):
        if self.history:
            prev_index = self.history.pop()
            self.stacked_widget.setCurrentIndex(prev_index)
            self.update_title(prev_index)
            self.back_button.setVisible(prev_index > 0)
            if prev_index == 0:
                self.load_products()
            elif prev_index == 1:
                self.update_total()
            elif prev_index == 2:
                self.load_orders()

    def update_title(self, index):
        titles = [
            "Мир здорового питания — Каталог",
            "Мир здорового питания — Корзина",
            "Мир здорового питания — Заказы"
        ]
        if 0 <= index < len(titles):
            self.setWindowTitle(titles[index])

    def load_orders(self):
        self.orders_table.setRowCount(0)
        if not self.user_id:
            return
        query = """
            SELECT o.order_id, o.order_date, p.name, oi.quantity, oi.price
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.user_id = %s
            ORDER BY o.order_id DESC
        """
        result = self.db.execute_query(query, (self.user_id,))
        if not result:
            return
        for row, data in enumerate(result):
            self.orders_table.insertRow(row)
            for col, value in enumerate(data):
                self.orders_table.setItem(row, col, QTableWidgetItem(str(value)))
            order_id = data[0]
            delete_btn = QPushButton("Удалить")
            delete_btn.setStyleSheet("background-color: #D32F2F; color: white; padding: 3px; border-radius: 3px;")
            delete_btn.clicked.connect(lambda checked, oid=order_id: self.delete_order(oid))
            self.orders_table.setCellWidget(row, 5, delete_btn)

    def delete_order(self, order_id):
        reply = QMessageBox.question(self, "Удаление заказа", 
            f"Вы уверены, что хотите удалить заказ №{order_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = self.db.get_connection()
            if not conn:
                return
            try:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
                cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
                conn.commit()
                cursor.close()
                QMessageBox.information(self, "Успех", f"Заказ №{order_id} удален")
                self.load_orders()
            except Exception as e:
                print(f"Ошибка при удалении заказа: {e}")
                conn.rollback()
            finally:
                self.db.release_connection(conn)

    def add_to_order(self, product_id, size_id):
        if not self.user_id:
            print("Ошибка: нет user_id")
            return
        conn = self.db.get_connection()
        if not conn:
            print("Ошибка: нет подключения к БД")
            return
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO orders (order_date, user_id) VALUES (CURRENT_DATE, %s) RETURNING order_id",
                (self.user_id,)
            )
            order_res = cursor.fetchone()
            if order_res is None: return
            order_id = order_res[0]
            cursor.execute("SELECT price FROM products WHERE product_id = %s", (product_id,))
            price_res = cursor.fetchone()
            if price_res is None: return
            price = price_res[0]
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, size_id, quantity, price) VALUES (%s, %s, %s, %s, %s)",
                (order_id, product_id, size_id, 1, price)
            )
            conn.commit()
            cursor.close()
            QMessageBox.information(self, "Успех", f"Заказ №{order_id} успешно оформлен!")
            self.load_products()
        except Exception as e:
            print(f"Ошибка при создании заказа: {e}")
            conn.rollback()
        finally:
            self.db.release_connection(conn)

    def setup_role_interface(self):
        for btn in [self.my_orders_button, self.manager_button, self.admin_button, self.cart_button]:
            btn.hide()
            btn.setEnabled(False)
        if self.role_id == 1:
            self.admin_button.show()
            self.admin_button.setEnabled(True)
            self.manager_button.show()
            self.manager_button.setEnabled(True)
            self.cart_button.show()
            self.cart_button.setEnabled(True)
        elif self.role_id == 2:
            self.manager_button.show()
            self.manager_button.setEnabled(True)
            self.cart_button.show()
            self.cart_button.setEnabled(True)
        elif self.role_id == 3:
            self.my_orders_button.show()
            self.my_orders_button.setEnabled(True)
            self.cart_button.show()
            self.cart_button.setEnabled(True)

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

    def reset_filters(self):
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
        self.search_input.blockSignals(False)
        self.filter_combo.blockSignals(False)
        self.manufacturer_combo.blockSignals(False)
        self.sort_combo.blockSignals(False)
        self.filter_checkbox.blockSignals(False)
        self.in_stock_checkbox.blockSignals(False)
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
        manufacturer = self.manufacturer_combo.currentText()
        sort_by = self.sort_combo.currentText()
        query = """
            SELECT p.product_id, c.name, p.name, p.price, p.image_path, p.manufacturer,
                   COALESCE(SUM(si.quantity), 0) AS total_quantity
            FROM products p
            JOIN categories c ON p.category_id = c.category_id
            LEFT JOIN stock_items si ON p.product_id = si.product_id
            WHERE (p.name ILIKE %s OR p.description ILIKE %s)
            AND (c.name = %s OR %s = 'Все категории')
            AND (p.manufacturer = %s OR %s = 'Все производители')
            GROUP BY p.product_id, c.name, p.name, p.price, p.image_path, p.manufacturer
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
        cursor.execute(query, (search_text, search_text, category, category, manufacturer, manufacturer))
        products = cursor.fetchall()
        cursor.execute("SELECT size_id, value FROM sizes ORDER BY size_id")
        sizes = cursor.fetchall()
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
            products_data.sort(key=lambda x: x[0][6] == 0)
        if self.filter_checkbox.isChecked():
            products_data = [item for item in products_data if item[1] > 15]
        if self.in_stock_checkbox.isChecked():
            products_data = [item for item in products_data if item[0][6] > 0]
        for product, discount, new_price in products_data:
            card = create_card(product, discount, new_price, sizes, self)
            self.scroll_layout.addWidget(card)
        self.scroll_area.setUpdatesEnabled(True)

    def logout(self):
        reply = QMessageBox.warning(self, "Предупреждение", "Вы уверены, что хотите выйти?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            from login_window import LoginWindow
            self.login_window = LoginWindow(self.db)
            self.login_window.show()
            self.close()

    def closeEvent(self, event):
        reply = QMessageBox.warning(self, "Предупреждение", "Вы уверены, что хотите выйти?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        with open("style_light.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Не удалось загрузить стили: {e}")
    db = Database()
    from login_window import LoginWindow
    login_window = LoginWindow(db)
    login_window.show()
    exit_code = app.exec()
    db.close_all()
    sys.exit(exit_code)