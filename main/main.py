import sys
import logging
from PyQt6.QtWidgets import QApplication
from config import load_config
from ui.main_window import MainWindow

def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='app.log',
        filemode='a'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        app = QApplication(sys.argv)
        window = MainWindow(config)
        window.showMaximized()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()