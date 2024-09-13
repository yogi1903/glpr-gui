from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QMessageBox)
from .base_page import BasePage
from database_manager import get_database_manager

class RemovePage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)
        self.db_manager = get_database_manager()

    def setup_content(self):
        layout = QVBoxLayout()

        # Vehicle Number Input
        self.vehicle_number_input = QLineEdit()
        self.vehicle_number_input.setPlaceholderText("Enter Vehicle Number to Remove")
        layout.addWidget(self.vehicle_number_input)

        # Remove Vehicle Button
        remove_button = QPushButton("Remove Vehicle")
        remove_button.clicked.connect(self.remove_vehicle)
        layout.addWidget(remove_button)

        self.content_layout.addLayout(layout)

    def remove_vehicle(self):
        try:
            vehicle_number = self.vehicle_number_input.text()

            if not vehicle_number:
                raise ValueError("Vehicle number is required")

            success = self.db_manager.delete_vehicle(vehicle_number)

            if success:
                QMessageBox.information(self, "Success", f"Vehicle {vehicle_number} removed successfully")
                self.vehicle_number_input.clear()
            else:
                QMessageBox.warning(self, "Error", f"Vehicle {vehicle_number} not found or could not be removed")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def go_back(self):
        self.main_window.show_page('manage')