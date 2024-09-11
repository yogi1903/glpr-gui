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
from ultralytics import YOLO
from paddleocr import PaddleOCR

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load and Assign Stylesheet
def load_stylesheet():
    with open('styles.qss', 'r') as file:
        return file.read()


stylesheet = load_stylesheet()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-LPR")
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.init_pages()

    def init_pages(self):
        self.main_page = MainPage(self)
        self.detect_page = DetectPage(self)
        self.manage_page = ManagePage(self)
        self.add_page = AddPage(self)
        self.remove_page = RemovePage(self)
        self.showall_page = ShowallPage(self)
        self.reports_page = ReportsPage(self)

        self.central_widget.addWidget(self.main_page)
        self.central_widget.addWidget(self.detect_page)
        self.central_widget.addWidget(self.manage_page)
        self.central_widget.addWidget(self.reports_page)
        self.central_widget.addWidget(self.add_page)
        self.central_widget.addWidget(self.remove_page)
        self.central_widget.addWidget(self.showall_page)

    def go_home(self):
        self.central_widget.setCurrentWidget(self.main_page)

    def show_manage(self):
        self.central_widget.setCurrentWidget(self.manage_page)

    def show_detect(self):
        self.central_widget.setCurrentWidget(self.detect_page)

    def show_reports(self):
        self.central_widget.setCurrentWidget(self.reports_page)

    def show_add(self):
        self.central_widget.setCurrentWidget(self.add_page)

    def show_remove(self):
        self.central_widget.setCurrentWidget(self.remove_page)

    def show_all(self):
        self.central_widget.setCurrentWidget(self.showall_page)

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)


class BasePage(QWidget):
    def __init__(self, main_window, title=None):
        super().__init__()
        self.main_window = main_window
        self.title = title
        self.create_layout()

    def create_layout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.create_nav_bar())

        # Create a QWidget to hold the top layout and set its background color
        top_widget = QWidget()
        top_widget.setStyleSheet("background-color: #007366;")
        top_layout = QGridLayout(top_widget)
        top_layout.setContentsMargins(20, 20, 20, 20)
        top_layout.setSpacing(0)

        # Create left image
        left_image_label = QLabel()
        left_pixmap = QPixmap('gitam_logo_green.jpeg').scaled(300, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation)
        left_image_label.setPixmap(left_pixmap)
        left_image_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Create right image
        right_image_label = QLabel()
        right_pixmap = QPixmap('indian_navy_logo.png').scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation)
        right_image_label.setPixmap(right_pixmap)
        right_image_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Create title label
        title_label = QLabel(self.title) if self.title else QLabel()
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #f4e4ca;")

        # Add widgets to top layout
        top_layout.addWidget(left_image_label, 0, 0)
        top_layout.addWidget(title_label, 0, 1)
        top_layout.addWidget(right_image_label, 0, 2)

        # Set column stretches to center the title
        top_layout.setColumnStretch(0, 1)
        top_layout.setColumnStretch(1, 2)
        top_layout.setColumnStretch(2, 1)

        layout.addWidget(top_widget)

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

        home_button = self.create_nav_button("Home", self.main_window.go_home)
        home_button.setStyleSheet(stylesheet)
        nav_layout.addWidget(home_button)

        brand_label = QLabel("G-FRS")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_label.setStyleSheet("font-size: 22px; font-weight: bold; color:#007366;")
        brand_label.setFont(QFont("Segoe UI", 14))
        nav_layout.addWidget(brand_label, 1)

        back_button = self.create_nav_button("Back", self.go_back)
        back_button.setStyleSheet(stylesheet)
        nav_layout.addWidget(back_button)

        return nav_bar

    def create_nav_button(self, text, on_click):
        button = QPushButton(text)
        button.setFont(QFont("Segoe UI", 10))
        button.clicked.connect(on_click)
        return button

    def setup_content(self):
        # To be implemented by subclasses
        pass

    def go_back(self):
        # To be implemented by subclasses
        pass


class MainPage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)

    def setup_content(self):
        buttons = [
            ("Detect", self.main_window.show_detect),
            ("Manage", self.main_window.show_manage),
            ("Reports", self.main_window.show_reports),
        ]

        for text, method in buttons:
            button = QPushButton(text)
            button.clicked.connect(method)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFixedHeight(50)
            self.content_layout.addWidget(button)


class DetectPage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)

    def go_back(self):
        self.main_window.central_widget.setCurrentWidget(self.main_window.main_page)


class ManagePage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)

    def setup_content(self):
        buttons = [
            ("Add Vehicle", self.main_window.show_add),
            ("Remove Vehicle", self.main_window.show_remove),
            ("Show all Vehicles", self.main_window.show_all),
        ]

        for text, method in buttons:
            button = QPushButton(text)
            button.clicked.connect(method)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFixedHeight(50)
            self.content_layout.addWidget(button)

    def go_back(self):
        self.main_window.central_widget.setCurrentWidget(self.main_window.main_page)


class AddPage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)

    def go_back(self):
        self.main_window.central_widget.setCurrentWidget(self.main_window.manage_page)


class RemovePage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)

    def go_back(self):
        self.main_window.central_widget.setCurrentWidget(self.main_window.manage_page)


class ShowallPage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)

    def go_back(self):
        self.main_window.central_widget.setCurrentWidget(self.main_window.manage_page)


class ReportsPage(BasePage):
    def __init__(self, main_window):
        super().__init__(main_window)

    def go_back(self):
        self.main_window.central_widget.setCurrentWidget(self.main_window.main_page)


if __name__ == '__main__':
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())
