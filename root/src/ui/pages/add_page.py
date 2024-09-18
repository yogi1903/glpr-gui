from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QMessageBox, QComboBox)
from .base_page import BasePage
from database_manager import get_database_manager

class AddPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)
        self.db_manager = get_database_manager()

    def setup_content(self):
        layout = QVBoxLayout()

        # Vehicle Number
        self.vehicle_number_input = QLineEdit()
        self.vehicle_number_input.setPlaceholderText("Vehicle Number")
        layout.addWidget(self.vehicle_number_input)

        # Vehicle Type
        self.vehicle_type_input = QLineEdit()
        self.vehicle_type_input.setPlaceholderText("Vehicle Type")
        layout.addWidget(self.vehicle_type_input)

        # Vehicle Color
        self.vehicle_color_input = QLineEdit()
        self.vehicle_color_input.setPlaceholderText("Vehicle Color")
        layout.addWidget(self.vehicle_color_input)

        # Owner Name
        self.owner_name_input = QLineEdit()
        self.owner_name_input.setPlaceholderText("Owner Name")
        layout.addWidget(self.owner_name_input)

        # Owner Aadhar
        self.owner_aadhar_input = QLineEdit()
        self.owner_aadhar_input.setPlaceholderText("Owner Aadhar")
        layout.addWidget(self.owner_aadhar_input)

        # Affiliation (Dropdown)
        self.affiliation_input = QComboBox()
        self.affiliation_input.addItems(["Navy", "Non-Navy"])
        layout.addWidget(QLabel("Affiliation:"))
        layout.addWidget(self.affiliation_input)

        # Add Vehicle Button
        add_button = QPushButton("Add Vehicle")
        add_button.clicked.connect(self.add_vehicle)
        layout.addWidget(add_button)

        self.content_layout.addLayout(layout)

    def add_vehicle(self):
        try:
            vehicle_number = self.vehicle_number_input.text()
            vehicle_type = self.vehicle_type_input.text()
            vehicle_color = self.vehicle_color_input.text()
            owner_name = self.owner_name_input.text()
            owner_aadhar = self.owner_aadhar_input.text()
            affiliation = self.affiliation_input.currentText()

            if not all([vehicle_number, vehicle_type, vehicle_color, owner_name, owner_aadhar]):
                raise ValueError("All fields are required")

            success = self.db_manager.add_vehicle(
                vehicle_number, vehicle_type, vehicle_color, owner_name, owner_aadhar, affiliation, ""
            )

            if success:
                QMessageBox.information(self, "Success", "Vehicle added successfully")
                self.clear_inputs()
            else:
                QMessageBox.warning(self, "Error", "Failed to add vehicle")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def clear_inputs(self):
        for widget in [self.vehicle_number_input, self.vehicle_type_input, self.vehicle_color_input,
                       self.owner_name_input, self.owner_aadhar_input]:
            widget.clear()
        self.affiliation_input.setCurrentIndex(0)  # Reset to first option

    def go_back(self):
        self.main_window.show_page('manage')