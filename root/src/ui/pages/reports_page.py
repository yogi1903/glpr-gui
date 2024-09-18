import csv
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QDateEdit, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView,
                             QMenu, QFileDialog)
from PyQt6.QtCore import Qt, QDate, QDateTime
from PyQt6.QtGui import QAction
from .base_page import BasePage
from database_manager import get_database_manager

class ReportsPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)
        self.db_manager = get_database_manager()
        self.current_page = 1
        self.items_per_page = 20
        self.total_items = 0
        self.current_logs = []

    def setup_content(self):
        layout = QVBoxLayout()

        # Quick report button
        quick_report_layout = QHBoxLayout()
        
        all_reports_button = QPushButton("All Reports")
        all_reports_button.clicked.connect(self.show_all_reports)
        quick_report_layout.addWidget(all_reports_button)

        layout.addLayout(quick_report_layout)

        # Filter form
        filter_layout = QHBoxLayout()

        self.vehicle_number_input = QLineEdit()
        self.vehicle_number_input.setPlaceholderText("Vehicle Number")
        filter_layout.addWidget(self.vehicle_number_input)

        self.start_date_input = QDateEdit()
        self.start_date_input.setCalendarPopup(True)
        self.start_date_input.setDate(QDate.currentDate().addDays(-30))  # Default to last 30 days
        filter_layout.addWidget(self.start_date_input)

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_input)

        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_reports)
        filter_layout.addWidget(search_button)

        layout.addLayout(filter_layout)

        # Status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Vehicle Number", "Entry Time", "Exit Time", "Duration"])
        
        # Set fixed column widths
        self.results_table.setColumnWidth(0, 150)  # Vehicle Number
        self.results_table.setColumnWidth(1, 200)  # Entry Time
        self.results_table.setColumnWidth(2, 200)  # Exit Time
        self.results_table.setColumnWidth(3, 100)  # Duration
        
        # Set the last column to stretch
        self.results_table.horizontalHeader().setStretchLastSection(True)
        
        # Set resize mode for all columns except the last one
        for i in range(self.results_table.columnCount() - 1):
            self.results_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)

        # Enable sorting
        self.results_table.setSortingEnabled(True)

        # Set alternating row colors
        self.results_table.setAlternatingRowColors(True)

        # Connect the header click event to the sorting method
        self.results_table.horizontalHeader().sectionClicked.connect(self.sort_table)

        layout.addWidget(self.results_table)

        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        # Page label (left-aligned)
        self.page_label = QLabel()
        pagination_layout.addWidget(self.page_label)
        
        # Spacer to push buttons to the right
        pagination_layout.addStretch()
        
        # Previous and Next buttons (right-aligned)
        button_layout = QHBoxLayout()
        self.prev_button = QPushButton("←")
        self.prev_button.setFixedSize(40, 30)
        self.prev_button.clicked.connect(self.previous_page)
        button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton("→")
        self.next_button.setFixedSize(40, 30)
        self.next_button.clicked.connect(self.next_page)
        button_layout.addWidget(self.next_button)

        pagination_layout.addLayout(button_layout)

        layout.addLayout(pagination_layout)

        # Export button
        export_button = QPushButton("Export to CSV")
        export_button.clicked.connect(self.export_to_csv)
        layout.addWidget(export_button)

        self.content_layout.addLayout(layout)

        # Set up context menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)

    def search_reports(self):
        try:
            vehicle_number = self.vehicle_number_input.text() or None
            start_date = self.start_date_input.dateTime().toString(Qt.DateFormat.ISODate)
            end_date = self.end_date_input.dateTime().addSecs(86399).toString(Qt.DateFormat.ISODate)  # End of the day

            if self.start_date_input.date() > self.end_date_input.date():
                raise ValueError("Start date cannot be after end date")

            self.current_logs = self.db_manager.get_entry_exit_logs(vehicle_number, start_date, end_date)
            self.total_items = len(self.current_logs)
            self.current_page = 1
            self.update_table()
            self.update_status_label()
            self.update_pagination_controls()
        except ValueError as e:
            self.show_error_message(str(e))
        except Exception as e:
            self.show_error_message(f"An error occurred while searching reports: {str(e)}")

    def show_all_reports(self):
        try:
            self.vehicle_number_input.clear()
            self.start_date_input.setDate(QDate(1900, 1, 1))  # Set to a very early date
            self.end_date_input.setDate(QDate.currentDate())
            self.search_reports()
        except Exception as e:
            self.show_error_message(f"An error occurred while showing all reports: {str(e)}")

    def update_table(self):
        start_index = (self.current_page - 1) * self.items_per_page
        end_index = min(start_index + self.items_per_page, self.total_items)
        page_logs = self.current_logs[start_index:end_index]

        self.results_table.setRowCount(len(page_logs))
        for row, log in enumerate(page_logs):
            vehicle_number = log[1]
            entry_time = log[2]
            exit_time = log[3] or "N/A"
            
            if exit_time != "N/A":
                duration = self.calculate_duration(entry_time, exit_time)
            else:
                duration = "N/A"

            self.results_table.setItem(row, 0, QTableWidgetItem(vehicle_number))
            self.results_table.setItem(row, 1, QTableWidgetItem(entry_time))
            self.results_table.setItem(row, 2, QTableWidgetItem(exit_time))
            self.results_table.setItem(row, 3, QTableWidgetItem(duration))

    def update_status_label(self):
        self.status_label.setText(f"Total results: {self.total_items}")

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

    def sort_table(self, column):
        self.results_table.sortItems(column, Qt.SortOrder.AscendingOrder)

    def calculate_duration(self, entry_time, exit_time):
        try:
            from datetime import datetime
            entry = datetime.strptime(entry_time, "%Y-%m-%d %H:%M:%S.%f")
            exit = datetime.strptime(exit_time, "%Y-%m-%d %H:%M:%S.%f")
            duration = exit - entry
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        except Exception as e:
            self.show_error_message(f"An error occurred while calculating duration: {str(e)}")
            return "Error"

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_context_menu(self, position):
        menu = QMenu()
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_cell_content)
        menu.addAction(copy_action)
        menu.exec(self.results_table.viewport().mapToGlobal(position))

    def copy_cell_content(self):
        selected_items = self.results_table.selectedItems()
        if selected_items:
            clipboard = QApplication.clipboard() # type: ignore
            clipboard.setText(selected_items[0].text())

    def export_to_csv(self):
        try:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
            if file_name:
                with open(file_name, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Vehicle Number", "Entry Time", "Exit Time", "Duration"])
                    for log in self.current_logs:
                        vehicle_number = log[1]
                        entry_time = log[2]
                        exit_time = log[3] or "N/A"
                        if exit_time != "N/A":
                            duration = self.calculate_duration(entry_time, exit_time)
                        else:
                            duration = "N/A"
                        writer.writerow([vehicle_number, entry_time, exit_time, duration])
                QMessageBox.information(self, "Export Successful", "The report has been exported to CSV successfully.")
        except Exception as e:
            self.show_error_message(f"An error occurred while exporting to CSV: {str(e)}")

    def go_back(self):
        self.main_window.show_page('main')