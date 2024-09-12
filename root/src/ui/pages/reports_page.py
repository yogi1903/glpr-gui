from .base_page import BasePage

class ReportsPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def setup_content(self):
        # TODO: Implement reports functionality
        pass

    def go_back(self):
        self.main_window.show_page('main')