from .base_page import BasePage

class DetectPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)

    def setup_content(self):
        # TODO: Implement license plate detection functionality
        pass

    def go_back(self):
        self.main_window.show_page('main')