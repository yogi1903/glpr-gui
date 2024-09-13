from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from .base_page import BasePage
from database_manager import get_database_manager

class ShowAllVehiclesPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)
        self.db_manager = get_database_manager()
        print("ShowAllVehiclesPage initialized with db_manager:", self.db_manager)

    def setup_content(self):
        layout = QVBoxLayout()

        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(7)  # 6 columns for data + 1 for delete button
        self.table.setHorizontalHeaderLabels([
            "Vehicle Number", "Vehicle Type", "Vehicle Color", 
            "Owner Name", "Owner Aadhar", "Affiliation", "Action"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)

        # Refresh button
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_vehicles)
        layout.addWidget(refresh_button)

        self.content_layout.addLayout(layout)

        # Load vehicles initially
        self.load_vehicles()

    def load_vehicles(self):
        try:
            vehicles = self.db_manager.get_all_vehicles()
            self.table.setRowCount(len(vehicles))
            for row, vehicle in enumerate(vehicles):
                for col, value in enumerate(vehicle[1:7]):  # Skip the ID column
                    self.table.setItem(row, col, QTableWidgetItem(str(value)))
                
                # Add delete button
                delete_button = QPushButton("Delete")
                delete_button.clicked.connect(lambda _, r=row, vn=vehicle[1]: self.delete_vehicle(r, vn))
                self.table.setCellWidget(row, 6, delete_button)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load vehicles: {str(e)}")

    def delete_vehicle(self, row, vehicle_number):
        reply = QMessageBox.question(self, 'Delete Vehicle', 
                                     f"Are you sure you want to delete vehicle {vehicle_number}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.db_manager.delete_vehicle(vehicle_number)
                if success:
                    self.table.removeRow(row)
                    QMessageBox.information(self, "Success", f"Vehicle {vehicle_number} deleted successfully")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete vehicle {vehicle_number}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def go_back(self):
        self.main_window.show_page('manage')