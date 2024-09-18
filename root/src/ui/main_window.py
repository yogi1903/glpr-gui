import logging
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QVBoxLayout
from PyQt6.QtGui import QFont
from typing import Dict, Any
from .pages.main_page import MainPage
from .pages.detect_page import DetectPage
from .pages.manage_page import ManagePage
from .pages.reports_page import ReportsPage
from .pages.show_all_vehicles_page import ShowAllVehiclesPage
from .pages.add_page import AddPage
from .pages.remove_page import RemovePage

class MainWindow(QMainWindow):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.setWindowTitle(self.config.get("app_title", "G-LPR"))
        self.setObjectName("mainWindow")
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("stackedWidget")
        main_layout.addWidget(self.stacked_widget)

        self.init_pages()

    def init_pages(self):
        try:
            self.pages = {
                'main': MainPage(self, "Main Page"),
                'detect': DetectPage(self, "Detect"),
                'manage': ManagePage(self, "Manage"),
                'add': AddPage(self, "Add Vehicle"),
                'remove': RemovePage(self, "Remove Vehicle"),
                'show_all': ShowAllVehiclesPage(self, "All Vehicles"),
                'reports': ReportsPage(self, "Reports")
            }
            for page in self.pages.values():
                self.stacked_widget.addWidget(page)
        except Exception as e:
            self.logger.error(f"Error initializing pages: {str(e)}", exc_info=True)
            raise

    def show_page(self, page_name: str):
        if page_name in self.pages:
            self.stacked_widget.setCurrentWidget(self.pages[page_name])
        else:
            self.logger.warning(f"Attempted to show non-existent page: {page_name}")

    def closeEvent(self, event):
        self.logger.info("Application closing")
        super().closeEvent(event)