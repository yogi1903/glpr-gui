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

# Load and Assign Stylesheet
def load_stylesheet():
    with open('stylesheet.qss', 'r') as file:
        return file.read()
stylesheet = load_stylesheet()

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class LicensePlateRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-LPR")
        self.setGeometry(100, 100, 1280, 720)

        self.csv_file = "license_plates.csv"
        self.is_processing = False
        self.is_popup_open = False

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.camera_tab = QWidget()
        self.reports_tab = QWidget()

        self.tab_widget.addTab(self.camera_tab, "Camera")
        self.tab_widget.addTab(self.reports_tab, "Reports")

        self.setup_camera_tab()
        self.setup_reports_tab()

        self.cap = None
        self.frame_buffer = deque(maxlen=10)  # Buffer to hold up to 10 frames
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture_frame)
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.display_frame)
        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.process_frame)

        # Load YOLO model for license plates
        self.license_plate_model = YOLO('models\\bestbest.pt')

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
            self.cap = cv2.VideoCapture(1)  # Use 0 for default camera
            self.is_processing = True
            self.capture_timer.start(30)  # Capture frame every 30 ms
            self.display_timer.start(30)  # Display frame every 30 ms
            self.process_timer.start(50)  # Process frame every 50 ms

    def stop_camera(self):
        self.is_processing = False
        self.capture_timer.stop()
        self.display_timer.stop()
        self.process_timer.stop()
        if self.cap:
            self.cap.release()
        self.cap = None
        self.camera_label.clear()
        self.frame_buffer.clear()
        
    def capture_frame(self):
        if self.cap and self.is_processing:
            ret, frame = self.cap.read()
            if ret:
                self.frame_buffer.append(frame)

    def process_frame(self):
        if self.is_processing and not self.is_popup_open and self.frame_buffer:
            frame = self.frame_buffer[-1]  # Get the latest frame
            license_plates = self.detect_license_plates(frame)
            for box, license_plate_img in license_plates:
                text = self.recognize_license_plate(license_plate_img)
                if text and self.is_valid_license_plate(text):
                    self.is_popup_open = True
                    self.show_popup(text, license_plate_img)
                    return  # Exit the method after showing the popup

            self.display_frame(frame)

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

    def display_frame(self):
        if self.frame_buffer:
            frame = self.frame_buffer[-1]  # Get the latest frame
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_image = cv2.resize(rgb_image, (1280, 720))
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_label.setPixmap(pixmap)

    def resume_processing(self):
        self.is_popup_open = False

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
    window = LicensePlateRecognitionApp()
    window.showMaximized()
    sys.exit(app.exec())
