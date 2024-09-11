import os
import sys
import csv
import re
import cv2
import logging
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QDate
from PyQt6.QtGui import QPixmap, QColor, QFont, QImage
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QPushButton, QLabel, QLineEdit, QComboBox, QRadioButton,
    QTableWidget, QTableWidgetItem, QListWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QFrame, QSizePolicy, QHeaderView, QButtonGroup,
    QMessageBox, QDialog, QCalendarWidget, QTextEdit, QInputDialog, QDateEdit, QFileDialog)
from functools import lru_cache

# Lazy imports
def import_yolo():
    from ultralytics import YOLO
    return YOLO

def import_paddleocr():
    from paddleocr import PaddleOCR
    return PaddleOCR

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@lru_cache(maxsize=1)
def load_stylesheet():
    with open('stylesheet.qss', 'r') as file:
        return file.read()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-LPR")
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.init_pages()

    def init_pages(self):
        self.pages = {
            'main': MainPage(self, "Main Page"),
            'detect': DetectPage(self, "Detect"),
            'manage': ManagePage(self, "Manage"),
            'add': AddPage(self, "Add Vehicle"),
            'remove': RemovePage(self, "Remove Vehicle"),
            'showall': ShowallPage(self, "All Vehicles"),
            'reports': ReportsPage(self, "Reports")
        }

        for page in self.pages.values():
            self.central_widget.addWidget(page)

    def show_page(self, page_name):
        self.central_widget.setCurrentWidget(self.pages[page_name])

    def closeEvent(self, event):
        # Perform any necessary cleanup here
        super().closeEvent(event)

class BasePage(QWidget):
    def __init__(self, main_window, title):
        super().__init__()
        self.main_window = main_window
        self.title = title
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.create_nav_bar())
        layout.addWidget(self.create_top_widget())

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(20)

        self.setup_content()

        self.content_layout.addStretch(1)
        layout.addWidget(self.content_widget)

    def create_nav_bar(self):
        nav_bar = QFrame()
        nav_bar.setStyleSheet("background-color: #f4e4ca; color:#007366;")
        nav_bar.setFixedHeight(60)

        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(20, 0, 20, 0)

        home_button = self.create_nav_button("Home", lambda: self.main_window.show_page('main'))
        nav_layout.addWidget(home_button)

        brand_label = QLabel("G-FRS")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_label.setStyleSheet("font-size: 22px; font-weight: bold; color:#007366;")
        brand_label.setFont(QFont("Segoe UI", 14))
        nav_layout.addWidget(brand_label, 1)

        back_button = self.create_nav_button("Back", self.go_back)
        nav_layout.addWidget(back_button)

        return nav_bar

    def create_top_widget(self):
        top_widget = QWidget()
        top_widget.setStyleSheet("background-color: #007366;")
        top_layout = QGridLayout(top_widget)
        top_layout.setContentsMargins(20, 20, 20, 20)
        top_layout.setSpacing(0)

        left_image_label = QLabel()
        left_pixmap = QPixmap('gitam_logo_green.jpeg').scaled(300, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation)
        left_image_label.setPixmap(left_pixmap)
        left_image_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        right_image_label = QLabel()
        right_pixmap = QPixmap('indian_navy_logo.png').scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation)
        right_image_label.setPixmap(right_pixmap)
        right_image_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #f4e4ca; font-size:32;")

        top_layout.addWidget(left_image_label, 0, 0)
        top_layout.addWidget(title_label, 0, 1)
        top_layout.addWidget(right_image_label, 0, 2)

        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 2)
        top_layout.setColumnStretch(2, 1)

        return top_widget

    @staticmethod
    def create_nav_button(text, on_click):
        button = QPushButton(text)
        button.setFont(QFont("Segoe UI", 10))
        button.clicked.connect(on_click)
        button.setStyleSheet(load_stylesheet())
        return button

    def setup_content(self):
        pass

    def go_back(self):
        pass

class MainPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def setup_content(self):
        buttons = [
            ("Detect", lambda: self.main_window.show_page('detect')),
            ("Manage", lambda: self.main_window.show_page('manage')),
            ("Reports", lambda: self.main_window.show_page('reports')),
        ]

        for text, method in buttons:
            button = QPushButton(text)
            button.clicked.connect(method)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFixedHeight(50)
            self.content_layout.addWidget(button)

class DetectPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def go_back(self):
        self.main_window.show_page('main')

class ManagePage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def setup_content(self):
        buttons = [
            ("Add Vehicle", lambda: self.main_window.show_page('add')),
            ("Remove Vehicle", lambda: self.main_window.show_page('remove')),
            ("Show all Vehicles", lambda: self.main_window.show_page('showall')),
        ]

        for text, method in buttons:
            button = QPushButton(text)
            button.clicked.connect(method)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFixedHeight(50)
            self.content_layout.addWidget(button)

    def go_back(self):
        self.main_window.show_page('main')

class AddPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def go_back(self):
        self.main_window.show_page('manage')

class RemovePage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def go_back(self):
        self.main_window.show_page('manage')

class ShowallPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def go_back(self):
        self.main_window.show_page('manage')

class ReportsPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def go_back(self):
        self.main_window.show_page('main')

if __name__ == '__main__':
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet())
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())