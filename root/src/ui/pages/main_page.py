from PyQt6.QtWidgets import QPushButton, QSizePolicy
from .base_page import BasePage

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

    def go_back(self):
        # This is the main page, so going back is not applicable
        pass