from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import logging
from typing import Callable

class BasePage(QWidget):
    def __init__(self, main_window, title: str):
        super().__init__()
        self.setObjectName(f"page{title.replace(' ', '')}")
        self.logger = logging.getLogger(__name__)
        self.main_window = main_window
        self.title = title
        self.config = main_window.config
        self.create_layout()

    def create_layout(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        main_layout.addWidget(self.create_nav_bar())
        main_layout.addWidget(self.create_top_widget())

        self.content_widget = QWidget()
        self.content_widget.setObjectName("contentWidget")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 40)
        self.content_layout.setSpacing(20)

        self.setup_content()

        self.content_layout.addStretch(1)
        main_layout.addWidget(self.content_widget)

    def create_nav_bar(self):
        nav_bar = QFrame()
        nav_bar.setObjectName("navBar")
        nav_bar.setFixedHeight(60)

        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(20, 0, 20, 0)

        home_button = self.create_nav_button("Home", lambda: self.main_window.show_page('main'))
        nav_layout.addWidget(home_button)

        brand_label = QLabel("G-FRS")
        brand_label.setObjectName("brandLabel")
        brand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_label.setFont(QFont("Segoe UI", 14))
        nav_layout.addWidget(brand_label, 1)

        back_button = self.create_nav_button("Back", self.go_back)
        nav_layout.addWidget(back_button)

        return nav_bar

    def create_top_widget(self):
        top_widget = QWidget()
        top_widget.setObjectName("topWidget")
        top_widget.setStyleSheet("background-color: #007366;")
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(20, 20, 20, 20)
        top_layout.setSpacing(0)

        left_image_label = QLabel()
        left_image_label.setObjectName("leftImageLabel")
        left_pixmap = QPixmap(self.config['images']['gitam_logo']).scaled(300, 100, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation)
        left_image_label.setPixmap(left_pixmap)
        left_image_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        title_label = QLabel(self.title)
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("color: #f4e4ca;")  # Set text color to light cream
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        title_font = QFont("Segoe UI", 24)
        title_font.setBold(True)
        title_label.setFont(title_font)

        right_image_label = QLabel()
        right_image_label.setObjectName("rightImageLabel")
        right_pixmap = QPixmap(self.config['images']['navy_logo']).scaled(100, 150, Qt.AspectRatioMode.KeepAspectRatio,
                                                              Qt.TransformationMode.SmoothTransformation)
        right_image_label.setPixmap(right_pixmap)
        right_image_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        top_layout.addWidget(left_image_label, 1)
        top_layout.addWidget(title_label, 2)  
        top_layout.addWidget(right_image_label, 1)

        return top_widget

    @staticmethod
    def create_nav_button(text: str, on_click: Callable[[], None]) -> QPushButton:
        button = QPushButton(text)
        button.setObjectName(f"navButton{text.replace(' ', '')}")
        button.setFont(QFont("Segoe UI", 10))
        button.clicked.connect(on_click)
        return button

    def setup_content(self):
        pass

    def go_back(self):
        pass