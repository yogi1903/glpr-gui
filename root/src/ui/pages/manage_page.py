from PyQt6.QtWidgets import QPushButton, QSizePolicy
from .base_page import BasePage

class ManagePage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def setup_content(self):
        buttons = [
            ("Add Vehicle", lambda: self.main_window.show_page('add')),
            ("Remove Vehicle", lambda: self.main_window.show_page('remove')),
            ("Show all Vehicles", self.show_all_vehicles),  # Changed this line
        ]

        for text, method in buttons:
            button = QPushButton(text)
            button.clicked.connect(method)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            button.setFixedHeight(50)
            self.content_layout.addWidget(button)

    def go_back(self):
        self.main_window.show_page('main')

    def show_all_vehicles(self):
        # Implement the functionality to show all vehicles here
        # For now, we'll just log a message
        self.logger.info("Show all vehicles functionality not yet implemented")