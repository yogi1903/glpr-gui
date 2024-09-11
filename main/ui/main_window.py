import logging
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from PyQt6.QtGui import QFont
from typing import Dict, Any
from .pages.main_page import MainPage
from .pages.detect_page import DetectPage
from .pages.manage_page import ManagePage
from .pages.reports_page import ReportsPage

class MainWindow(QMainWindow):
    def __init__(self, config: Dict[str, Any]):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.setWindowTitle(self.config.get("app_title", "G-LPR"))
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)
        self.init_pages()

    def init_pages(self):
        try:
            self.pages = {
                'main': MainPage(self, "Main Page"),
                'detect': DetectPage(self, "Detect"),
                'manage': ManagePage(self, "Manage"),
                'reports': ReportsPage(self, "Reports")
            }
            for page in self.pages.values():
                self.central_widget.addWidget(page)
        except Exception as e:
            self.logger.error(f"Error initializing pages: {str(e)}", exc_info=True)
            raise

    def show_page(self, page_name: str):
        if page_name in self.pages:
            self.central_widget.setCurrentWidget(self.pages[page_name])
        else:
            self.logger.warning(f"Attempted to show non-existent page: {page_name}")

    def closeEvent(self, event):
        self.logger.info("Application closing")
        # Perform any necessary cleanup here
        super().closeEvent(event)