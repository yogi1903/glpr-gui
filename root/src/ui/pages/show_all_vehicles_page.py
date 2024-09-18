from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QFormLayout,
                             QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QIcon
from .base_page import BasePage
from database_manager import get_database_manager
from fuzzywuzzy import fuzz
import csv

class ShowAllVehiclesPage(BasePage):
    def __init__(self, main_window, title):
        self.db_manager = get_database_manager()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.current_page = 1
        self.items_per_page = 20  # Initialize items_per_page here
        self.total_items = 0
        self.current_vehicles = []
        super().__init__(main_window, title)

    def setup_content(self):
        # Search bar and refresh button
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search vehicles...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)

        refresh_button = QPushButton("Refresh")
        refresh_button.setIcon(QIcon("path/to/refresh_icon.png"))  # Add path to your refresh icon
        refresh_button.clicked.connect(self.refresh_table)
        search_layout.addWidget(refresh_button)

        self.content_layout.addLayout(search_layout)

        # Table for displaying vehicles
        self.vehicles_table = QTableWidget()
        self.vehicles_table.setColumnCount(8)
        self.vehicles_table.setHorizontalHeaderLabels(["Vehicle Number", "Type", "Color", "Owner Name", "Owner Aadhar", "Affiliation", "Edit", "Delete"])
        self.vehicles_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.vehicles_table.verticalHeader().setDefaultSectionSize(50)  # Set default row height
        self.vehicles_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # Disable direct editing
        self.content_layout.addWidget(self.vehicles_table)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        # Page label (left-aligned)
        self.page_label = QLabel()
        pagination_layout.addWidget(self.page_label)
        
        # Spacer to push buttons to the right
        pagination_layout.addStretch()
        
        # Previous and Next buttons (right-aligned)
        self.prev_button = QPushButton("←")
        self.prev_button.setFixedSize(40, 30)
        self.prev_button.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("→")
        self.next_button.setFixedSize(40, 30)
        self.next_button.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_button)

        self.content_layout.addLayout(pagination_layout)

        # Export to CSV button (bottom right corner)
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        export_layout.addWidget(export_button)
        self.content_layout.addLayout(export_layout)

        # Load vehicles
        self.load_vehicles()

    def load_vehicles(self, search_term=None):
        self.current_vehicles = self.db_manager.get_all_vehicles()
        self.total_items = len(self.current_vehicles)
        self.current_page = 1
        self.update_table(search_term)
        self.update_pagination_controls()

    def update_table(self, search_term=None):
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = min(start_index + self.items_per_page, self.total_items)
        page_vehicles = self.current_vehicles[start_index:end_index]

        self.vehicles_table.setRowCount(0)
        for row, vehicle in enumerate(page_vehicles):
            if search_term:
                match_score = max(
                    fuzz.partial_ratio(search_term.lower(), str(field).lower())
                    for field in vehicle
                )
                if match_score < 70:  # Adjust threshold as needed
                    continue

            self.vehicles_table.insertRow(row)
            self.vehicles_table.setRowHeight(row, 50)  # Set row height to 50 pixels

            for col, value in enumerate(vehicle[:6]):  # Exclude image_path
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
                self.vehicles_table.setItem(row, col, item)

            # Edit button
            edit_button = QPushButton("Edit")
            edit_button.clicked.connect(lambda checked, r=row: self.edit_vehicle(r))
            self.vehicles_table.setCellWidget(row, 6, edit_button)

            # Delete button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(lambda checked, r=row: self.delete_vehicle(r))
            self.vehicles_table.setCellWidget(row, 7, delete_button)

    def on_search_text_changed(self):
        self.search_timer.start(300)  # Debounce for 300ms

    def perform_search(self):
        search_term = self.search_input.text()
        self.load_vehicles(search_term)

    def refresh_table(self):
        self.search_input.clear()
        self.load_vehicles()

    def edit_vehicle(self, row):
        vehicle_number = self.vehicles_table.item(row, 0).text()
        vehicle_data = self.db_manager.get_vehicle(vehicle_number)
        
        if vehicle_data:
            dialog = EditVehicleDialog(vehicle_data, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_updated_data()
                if self.db_manager.edit_vehicle(vehicle_number, *updated_data):
                    self.load_vehicles()  # Reload the table to reflect changes
                    QMessageBox.information(self, "Success", f"Vehicle {vehicle_number} updated successfully")
                else:
                    QMessageBox.warning(self, "Error", f"Failed to update vehicle {vehicle_number}")
        else:
            QMessageBox.warning(self, "Error", f"Vehicle {vehicle_number} not found")
            
    def delete_vehicle(self, row):
        vehicle_number = self.vehicles_table.item(row, 0).text()
        confirm = QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete vehicle {vehicle_number}?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_vehicle(vehicle_number):
                self.load_vehicles()  # Reload the table to reflect changes
                QMessageBox.information(self, "Success", f"Vehicle {vehicle_number} deleted successfully")
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete vehicle {vehicle_number}")

    def update_pagination_controls(self):
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        self.page_label.setText(f"Page {self.current_page} of {total_pages}")
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < total_pages)

    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_table()
            self.update_pagination_controls()

    def next_page(self):
        total_pages = (self.total_items + self.items_per_page - 1) // self.items_per_page
        if self.current_page < total_pages:
            self.current_page += 1
            self.update_table()
            self.update_pagination_controls()

    def export_to_csv(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if file_name:
                with open(file_name, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Vehicle Number", "Type", "Color", "Owner Name", "Owner Aadhar", "Affiliation"])
                    for vehicle in self.current_vehicles:
                        writer.writerow(vehicle[:6])  # Exclude image_path
                QMessageBox.information(self, "Export Successful", "The vehicle data has been exported to CSV successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred while exporting to CSV: {str(e)}")

    def go_back(self):
        self.main_window.show_page('manage')

class EditVehicleDialog(QDialog):
    def __init__(self, vehicle_data, parent=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data
        self.setWindowTitle("Edit Vehicle")
        self.setup_ui()

    def setup_ui(self):
        layout = QFormLayout(self)
        self.fields = {}

        field_names = ["vehicle_number", "vehicle_type", "vehicle_color", "owner_name", "owner_aadhar", "affiliation", "image_path"]
        for i, field in enumerate(field_names):
            if field != 'vehicle_number':  # We don't want to edit the vehicle number
                self.fields[field] = QLineEdit(str(self.vehicle_data[i]))
                self.fields[field].setText(str(self.vehicle_data[i]))  # Ensure the actual value is set
                layout.addRow(field.replace('_', ' ').title(), self.fields[field])

        buttons = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addRow(buttons)

    def get_updated_data(self):
        return tuple(widget.text() for field, widget in self.fields.items())