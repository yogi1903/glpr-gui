import sys
import logging
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile, QTextStream
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

def load_stylesheet(path):
    logger = logging.getLogger(__name__)
    logger.info(f"Attempting to load stylesheet from: {path}")
    if not os.path.exists(path):
        logger.error(f"Stylesheet file does not exist: {path}")
        return ""
    
    file = QFile(path)
    if not file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        logger.error(f"Failed to open stylesheet file: {path}")
        return ""
    
    stream = QTextStream(file)
    stylesheet = stream.readAll()
    logger.info(f"Stylesheet loaded successfully. Length: {len(stylesheet)} characters")
    return stylesheet

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        app = QApplication(sys.argv)
        
        # Load and apply stylesheet
        stylesheet = load_stylesheet(config['stylesheet_path'])
        app.setStyleSheet(stylesheet)
        
        window = MainWindow(config)
        window.showMaximized()
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()