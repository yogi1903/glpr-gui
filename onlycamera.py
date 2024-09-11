import os
import sys
import csv
import re
import cv2
import logging
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, \
    QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt
from ultralytics import YOLO
from paddleocr import PaddleOCR
from collections import deque
from threading import Thread, Lock
import time
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

stylesheet = """
    QWidget {
        background-color: #f4e4ca;
    }
    QPushButton {
        background-color: #007366;
        color: #f4e4ca;
        border-radius: 6px;
        border: 1px solid #007366;
        padding: 10px;
        text-align: center;
        font-family: 'Segoe UI';
        font-size: 14px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #01371C;
    }
    QPushButton:pressed {
        background-color: #309A65;
    }
    
    QFormLayout {
        margin: 20px;
    }
    QLabel {
        color: #007366;
        font-family: 'Segoe UI';
        font-size: 14px;
        font-weight: bold;
        text-align: center;
    }
    QLineEdit {
        border: 1px solid #007366;
        background-color: #f4e4ca;
        border-radius: 4px;
        padding: 8px;
        font-family: 'Segoe UI';
        font-size: 14px;
        color: #007366;
    }
    QLineEdit:focus {
        color: #f4e4ca;
        border-color: #309A65;
        background-color: #007366;
        font-family: 'Segoe UI';
        font-size: 14px;
        font-weight: bold;
    }
    QComboBox {
        border: 1px solid #007366;
        border-radius: 4px;
        padding: 8px;
        font-family: 'Segoe UI';
        font-size: 14px;
        color: #007366;
        background-color: #f4e4ca;
    }
    QComboBox QAbstractItemView {
        border: 1px solid #007366;
        border-radius: 4px;
        background-color: #f4e4ca;
        selection-background-color: #046A38;
        selection-color: #f4e4ca;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        background-color: #f4e4ca;
        border-left-width: 1px;
        border-left-color: #007366;
        border-left-style: solid;
        border-top-right-radius: 4px;
        border-bottom-right-radius: 4px;
    }
    QComboBox::down-arrow {
        image: url(down_arrow.png);  /* You can use a custom down arrow image */
    }
    QListView {
        background-color: #f4e4ca;
        border: 1px solid #007366;
        font-family: 'Segoe UI';
        font-size: 14px;
        color: #007366;
        selection-background-color: #046A38;
        selection-color: #f4e4ca;
    }
    QTableWidget {
        background-color: #007366;;
        border: 1px solid #007366;
        border-radius: 4px;
        font-family: 'Segoe UI';
        font-size: 14px;
        color: #f4e4ca;
        gridline-color: #004038;
    }
    QHeaderView::section {
        background-color: #007366;
        color: #f4e4ca;
        padding: 4px;
        border: 1px solid #004038;
        font-family: 'Segoe UI';
        font-size: 14px;
        font-weight: bold;
    }
    QTableWidget::item {
        padding: 4px;
        border: none;
        background-color: #007366;
    }
    QTableWidget::item:selected {
        background-color: #309A65;
        color: #f4e4ca;
    }
    QTableWidget QTableCornerButton::section {
        background-color: #007366;
        border: 1px solid #004038;
    }
    QScrollBar:vertical {
        border: 1px solid #004038;
        background: #007366;
        width: 15px;
        margin: 22px 0 22px 0;
    }
    QScrollBar::handle:vertical {
        background: #007366;
        min-height: 20px;
    }
    QScrollBar::add-line:vertical {
        border: 1px solid #007366;
        background: #f4e4ca;
        height: 20px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        border: 1px solid #007366;
        background: #f4e4ca;
        height: 20px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
        border: 1px solid #007366;
        width: 3px;
        height: 3px;
        background: #007366;
    }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
        background: none;
    }
    QListWidget{
        background-color: #007366;;
        border: 1px solid #007366;
        border-radius: 4px;
        font-family: 'Segoe UI';
        font-size: 14px;
        color: #f4e4ca;
        gridline-color: #004038;
    }
    QDateEdit {
    background-color: #f4e4ca;
    color: #007366;
    font-family: 'Segoe UI';
    font-weight: bold;
    font-size: 14px;
    padding: 5px;
    border: 1px solid #004038;
    border-radius: 5px;
    min-width: 100px;
}

QDateEdit::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border: none;
    background-color: #007366;
}

QDateEdit QAbstractItemView {
    border: 1px solid #004038;
    background-color: #007366;
    selection-background-color: #004038;
    selection-color: #f4e4ca;
    color: #f4e4ca;
}
QCalendarWidget {
    background-color: #007366;
    color: #f4e4ca;
    font-family: 'Segoe UI';
    font-weight: bold;
    border: 1px solid #004038;
    border-radius: 5px;
}

QCalendarWidget QAbstractItemView {
    border: 1px solid #004038;
    background-color: #007366;
    selection-background-color: #004038;
    selection-color: #f4e4ca;
    color: #f4e4ca;
}

QCalendarWidget QToolButton {
    background-color: #007366;
    border: none;
    color: #f4e4ca;
    font-family: 'Segoe UI';
    font-weight: bold;
}

QCalendarWidget QToolButton::menu-indicator {
    image: none; /* Remove the arrow */
}

QCalendarWidget QSpinBox {
    background-color: #007366;
    color: #f4e4ca;
    font-family: 'Segoe UI';
    font-weight: bold;
    border: 1px solid #004038;
}

QCalendarWidget QSpinBox::up-button,
QCalendarWidget QSpinBox::down-button {
    background-color: #007366;
    border: none;
}

QCalendarWidget QSpinBox::up-arrow,
QCalendarWidget QSpinBox::down-arrow {
    image: none; /* Remove the arrow */
}

QCalendarWidget QWidget#qt_calendar_navigationbar {
    background-color: #007366;
    border-bottom: 1px solid #004038;
}

QCalendarWidget QAbstractItemView::item {
    background-color: #007366;
    color: #f4e4ca;
    border: 1px solid #007366;
    border-radius: 5px;
}

QCalendarWidget QAbstractItemView::item:selected {
    background-color: #004038;
    color: #f4e4ca;
}
QTabWidget::pane {
    border: 1px solid #007366;
    background-color: #f4e4ca;
    border-radius: 6px;
}

QTabWidget::tab-bar {
    left: 5px;
}

QTabBar::tab {
    background-color: #007366;
    color: #f4e4ca;
    border: 1px solid #004038;
    border-bottom-color: #007366;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 12px;
    margin-right: 2px;
    font-family: 'Segoe UI';
    font-size: 14px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #f4e4ca;
    color: #007366;
    border: 1px solid #007366;
    border-bottom-color: #f4e4ca;
}

QTabBar::tab:!selected {
    margin-top: 2px;
}

QTabBar::tab:hover {
    background-color: #01371C;
    color: #f4e4ca;
}

QTabBar::tab:selected:hover {
    background-color: #309A65;
    color: #f4e4ca;
}

QTabWidget::tab-bar:top {
    top: 1px;
}f

QTabWidget::tab-bar:bottom {
    bottom: 1px;
}

QTabWidget::tab-bar:left {
    right: 1px;
}

QTabWidget::tab-bar:right {
    left: 1px;
}
"""


class LicensePlateRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-LPR")
        self.setGeometry(100, 100, 1280, 720)

        self.csv_file = "license_plates.csv"
        self.is_processing = False

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.camera_tab = QWidget()
        self.reports_tab = QWidget()

        self.tab_widget.addTab(self.camera_tab, "Camera")
        self.tab_widget.addTab(self.reports_tab, "Reports")

        self.setup_camera_tab()
        self.setup_reports_tab()

        self.cap = None
        self.frame_buffer = deque(maxlen=1)  # Only keep the latest frame
        self.buffer_lock = Lock()

        # Load YOLO model for license plates
        self.license_plate_model = YOLO('bestbest.pt')

        # Initialize PaddleOCR
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)

    def setup_camera_tab(self):
        self.camera_layout = QVBoxLayout(self.camera_tab)

        self.camera_label = QLabel()
        self.camera_layout.addWidget(self.camera_label)

        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        self.camera_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        self.camera_layout.addWidget(self.stop_button)

    def setup_reports_tab(self):
        self.reports_layout = QVBoxLayout(self.reports_tab)

        self.reports_table = QTableWidget()
        self.reports_table.setColumnCount(3)
        self.reports_table.setHorizontalHeaderLabels(["Timestamp", "Recognized Text", "Corrected Text"])
        self.reports_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.reports_layout.addWidget(self.reports_table)

        self.load_reports_data()

    def load_reports_data(self):
        try:
            if os.path.exists(self.csv_file):
                with open(self.csv_file, 'r') as file:
                    reader = csv.DictReader(file)
                    data = list(reader)

                if not data:
                    self.show_no_data()
                else:
                    self.reports_table.setRowCount(len(data))
                    for row, item in enumerate(data):
                        self.reports_table.setItem(row, 0, QTableWidgetItem(str(item.get('timestamp', ''))))
                        self.reports_table.setItem(row, 1, QTableWidgetItem(str(item.get('recognized_text', ''))))
                        self.reports_table.setItem(row, 2, QTableWidgetItem(str(item.get('corrected_text', ''))))
            else:
                self.show_no_data()
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            self.show_no_data()

    def show_no_data(self):
        self.reports_table.setRowCount(1)
        self.reports_table.setItem(0, 0, QTableWidgetItem("No data available"))
        self.reports_table.setItem(0, 1, QTableWidgetItem(""))
        self.reports_table.setItem(0, 2, QTableWidgetItem(""))

    def start_camera(self):
        if self.cap is None:
            # self.cap = cv2.VideoCapture("rtsp://admin:abcd1234@192.168.1.250:554/cam/realmonitor?channel=1&subtype=0")
            self.cap = cv2.VideoCapture(1)
            self.is_processing = True
            self.stream_thread = Thread(target=self._stream_frames)
            self.stream_thread.start()
            self.processing_thread = Thread(target=self._process_frames)
            self.processing_thread.start()

    def stop_camera(self):
        self.is_processing = False
        if self.stream_thread:
            self.stream_thread.join()
        if self.processing_thread:
            self.processing_thread.join()
        if self.cap:
            self.cap.release()
        self.cap = None
        self.camera_label.clear()

    def _stream_frames(self):
        while self.is_processing:
            ret, frame = self.cap.read()
            if ret:
                with self.buffer_lock:
                    self.frame_buffer.clear()
                    self.frame_buffer.append(frame)
            time.sleep(0.01)  # Small delay to prevent excessive CPU usage

    def _process_frames(self):
        while self.is_processing:
            with self.buffer_lock:
                if self.frame_buffer:
                    frame = self.frame_buffer.pop()
                else:
                    continue

            license_plates = self.detect_license_plates(frame)
            for box, license_plate_img in license_plates:
                text = self.recognize_license_plate(license_plate_img)
                if text and self.is_valid_license_plate(text):
                    self.show_popup(text, license_plate_img)
                    break  # Exit the loop after showing the popup

            self.display_frame(frame)
            time.sleep(0.03)  # Adjust this value to control processing rate

    def detect_license_plates(self, image):
        results = self.license_plate_model(image)
        license_plates = []
        for box in results[0].boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            license_plate_img = image[y1:y2, x1:x2]
            license_plates.append((box, license_plate_img))
        return license_plates

    def recognize_license_plate(self, image):
        result = self.ocr.ocr(image, cls=True)
        if result[0]:
            return ''.join([line[1][0] for line in result[0]])
        return None

    def is_valid_license_plate(self, text):
        # Implement your license plate validation logic here
        return bool(text)

    def show_popup(self, recognized_text, license_plate_img):
        popup = RecognitionPopup(recognized_text, license_plate_img, self)
        popup.show()

    def save_to_csv(self, recognized_text, corrected_text):
        fieldnames = ["timestamp", "recognized_text", "corrected_text"]
        data = {
            "timestamp": datetime.now().isoformat(),
            "recognized_text": recognized_text,
            "corrected_text": corrected_text
        }

        file_exists = os.path.exists(self.csv_file)

        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)

        self.load_reports_data()

    def display_frame(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_image = cv2.resize(rgb_image, (1280, 720))
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_label.setPixmap(pixmap)

    def resume_processing(self):
        self.is_processing = True

class RecognitionPopup(QWidget):
    def __init__(self, recognized_text, license_plate_img, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("License Plate Recognized")
        self.setGeometry(200, 200, 400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()

        # Display the license plate image
        self.frame_label = QLabel()
        self.display_license_plate(license_plate_img)
        layout.addWidget(self.frame_label)

        self.text_input = QLineEdit(recognized_text)
        layout.addWidget(self.text_input)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_text)
        button_layout.addWidget(save_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.recognized_text = recognized_text  # Save the recognized text

    def display_license_plate(self, license_plate_img):
        rgb_image = cv2.cvtColor(license_plate_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.frame_label.setPixmap(pixmap.scaled(380, 200, Qt.AspectRatioMode.KeepAspectRatio))

    def save_text(self):
        corrected_text = self.text_input.text()
        self.parent.save_to_csv(self.recognized_text, corrected_text)
        self.close()
        self.parent.resume_processing()

    def closeEvent(self, event):
        self.parent.resume_processing()
        super().closeEvent(event)


if __name__ == '__main__':
    os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    app = QApplication(sys.argv)
    app.setStyleSheet(stylesheet)
    window = LicensePlateRecognitionApp()
    window.showMaximized()
    sys.exit(app.exec())
