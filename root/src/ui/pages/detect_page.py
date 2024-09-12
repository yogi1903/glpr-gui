import cv2
import os
from PyQt6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QLineEdit, QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QTimer, Qt
from .base_page import BasePage
from ultralytics import YOLO
from paddleocr import PaddleOCR
from collections import deque
from database_manager import get_database_manager
from datetime import datetime

class DetectPage(BasePage):
    def __init__(self, main_window, title):
        super().__init__(main_window, title)
        self.setup_models()
        self.setup_camera()
        self.db_manager = get_database_manager()
        self.is_processing = False
        self.is_popup_open = False

    def setup_content(self):
        # Camera feed
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.camera_label)

        # Buttons layout
        button_layout = QHBoxLayout()

        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        button_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop Camera")
        self.stop_button.clicked.connect(self.stop_camera)
        button_layout.addWidget(self.stop_button)

        self.content_layout.addLayout(button_layout)

    def setup_models(self):
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', self.config['models']['license_plate'])
        self.license_plate_model = YOLO(model_path)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=True)

    def setup_camera(self):
        self.cap = None
        self.frame_buffer = deque(maxlen=10)
        self.capture_timer = QTimer(self)
        self.capture_timer.timeout.connect(self.capture_frame)
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.display_frame)
        self.process_timer = QTimer(self)
        self.process_timer.timeout.connect(self.process_frame)

    def start_camera(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.config['camera']['index'])
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['camera']['width'])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['camera']['height'])
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

    def display_frame(self):
        if self.frame_buffer:
            frame = self.frame_buffer[-1]  # Get the latest frame
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)
            self.camera_label.setPixmap(pixmap.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio))

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

    def save_to_database(self, recognized_text, corrected_text):
        # Save the license plate image
        image_path = os.path.join(self.config['license_plates_dir'], f"{corrected_text}.jpg")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, cv2.cvtColor(self.frame_buffer[-1], cv2.COLOR_BGR2RGB))

        # Check if the vehicle exists in the database
        vehicle = self.db_manager.get_vehicle(corrected_text)
        if not vehicle:
            # Add new vehicle to the database
            self.db_manager.add_vehicle(
                corrected_text, "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", image_path
            )

        # Log entry/exit
        self.db_manager.log_entry_exit(corrected_text)

    def resume_processing(self):
        self.is_popup_open = False

    def go_back(self):
        self.stop_camera()
        self.main_window.show_page('main')

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)


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
        self.parent.save_to_database(self.recognized_text, corrected_text)
        self.parent.resume_processing()  # Resume processing before closing
        self.close()  # Close the popup

    def closeEvent(self, event):
        self.parent.resume_processing()
        super().closeEvent(event)