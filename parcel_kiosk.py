import os
import sys
import csv
from datetime import datetime

import cv2
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QFrame,
    QHBoxLayout,
    QSizePolicy,
)

APP_BG = "#ecfdf3"
PRIMARY = "#16a34a"
PRIMARY_DARK = "#15803d"
PRIMARY_SOFT = "#dcfce7"
TEXT_MAIN = "#052e16"
TEXT_SUB = "#4b5563"
ADMIN_PASSWORD = "admin123"
APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(APP_DIR, "Nilailogo.png")


class ParcelWorkbook:
    HEADERS = ["Number", "Parcel ID", "Timestamp", "Photo Directory"]

    def __init__(self, path):
        self.path = path

    def ensure_workbook(self):
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(self.HEADERS)
            return

        with open(self.path, "r", newline="", encoding="utf-8") as handle:
            reader = csv.reader(handle)
            first_row = next(reader, None)

        if first_row != self.HEADERS:
            raise ValueError("Record file headers do not match expected format")

    def append_record(self, parcel_id, photo_path, timestamp):
        self.ensure_workbook()

        with open(self.path, "r", newline="", encoding="utf-8") as handle:
            record_number = sum(1 for _ in csv.reader(handle))

        with open(self.path, "a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow([record_number, parcel_id, timestamp, photo_path])

        return {
            "number": record_number,
            "parcel_id": parcel_id,
            "timestamp": timestamp,
            "photo_path": photo_path,
        }

    def read_records(self):
        self.ensure_workbook()
        with open(self.path, "r", newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            return list(reader)


def build_logo_label(width=220, height=110):
    label = QLabel()
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    if os.path.exists(LOGO_PATH):
        pixmap = QPixmap(LOGO_PATH)
        if not pixmap.isNull():
            label.setPixmap(
                pixmap.scaled(
                    width,
                    height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            return label

    label.setText("Nilai Logo")
    label.setStyleSheet(f"color: {TEXT_SUB};")
    return label


class ScanPage(QWidget):
    next_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal()

    def __init__(self, title, subtitle, next_button_text="Next"):
        super().__init__()
        self.camera = None
        self.current_frame = None
        self.detected_value = None
        self.scan_enabled = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.setStyleSheet(f"background-color: {APP_BG};")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(1200, 700)
        container.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f0fdf4
                );
                border-radius: 30px;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {TEXT_MAIN};")

        subtitle_label = QLabel(subtitle)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 14))
        subtitle_label.setStyleSheet(f"color: {TEXT_SUB};")

        scan_area = QFrame()
        scan_area.setStyleSheet(
            f"""
            QFrame {{
                background-color: {PRIMARY_SOFT};
                border-radius: 24px;
            }}
            """
        )

        scan_layout = QVBoxLayout(scan_area)
        scan_layout.setContentsMargins(24, 24, 24, 24)
        scan_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scan_layout.setSpacing(16)

        self.camera_label = QLabel("Opening camera...")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumHeight(500)
        self.camera_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.camera_label.setScaledContents(False)
        self.camera_label.setStyleSheet(
            """
            background-color: #cfead8;
            border-radius: 20px;
            color: #4b5563;
            font-size: 18px;
            font-weight: 600;
            """
        )

        self.status = QLabel("Live camera preview")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Arial", 15))
        self.status.setStyleSheet(
            f"""
            background: #bbf7d0;
            color: {PRIMARY_DARK};
            border-radius: 16px;
            padding: 10px 20px;
            """
        )

        scan_layout.addStretch(1)
        scan_layout.addWidget(self.camera_label, stretch=8)
        scan_layout.addWidget(self.status, stretch=1)
        scan_layout.addStretch(1)

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons.setSpacing(16)

        self.next_btn = QPushButton(next_button_text)
        self.next_btn.setFixedSize(220, 55)
        self.next_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_DARK};
            }}
            """
        )
        self.next_btn.clicked.connect(self.handle_next)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(180, 55)
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
            }
            """
        )
        cancel_btn.clicked.connect(self.cancel_requested.emit)

        buttons.addWidget(self.next_btn)
        buttons.addWidget(cancel_btn)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addWidget(scan_area, stretch=1)
        layout.addLayout(buttons)

        root.addWidget(container)
        self.setLayout(root)

    def handle_next(self):
        if self.detected_value:
            self.next_requested.emit(self.detected_value)

    def set_detected(self, value):
        if self.detected_value:
            return
        self.detected_value = value
        self.status.setText(f"Detected: {value}")
        self.status.setStyleSheet(
            f"""
            background: #86efac;
            color: {PRIMARY_DARK};
            border-radius: 16px;
            padding: 10px 20px;
            font-weight: bold;
            """
        )
        QTimer.singleShot(600, self.handle_next)

    def reset_scan_state(self, message="Live camera preview"):
        self.detected_value = None
        self.status.setText(message)
        self.status.setStyleSheet(
            f"""
            background: #bbf7d0;
            color: {PRIMARY_DARK};
            border-radius: 16px;
            padding: 10px 20px;
            """
        )

    def start_camera(self):
        if self.camera is not None and self.camera.isOpened():
            return

        self.camera = self.open_camera()
        if not self.camera.isOpened():
            self.camera_label.setText("Unable to open camera")
            self.status.setText("Camera not available")
            return

        self.timer.start(30)

    def open_camera(self):
        candidates = [(0, None)]
        if sys.platform == "darwin":
            candidates = [
                (0, cv2.CAP_AVFOUNDATION),
                (1, cv2.CAP_AVFOUNDATION),
                (0, None),
                (1, None),
            ]

        for index, backend in candidates:
            camera = cv2.VideoCapture(index) if backend is None else cv2.VideoCapture(index, backend)
            if camera is not None and camera.isOpened():
                return camera
            if camera is not None:
                camera.release()

        return cv2.VideoCapture()

    def stop_camera(self):
        self.timer.stop()
        if self.camera is not None:
            self.camera.release()
            self.camera = None
        self.camera_label.clear()
        self.camera_label.setText("Camera stopped")

    def update_frame(self):
        if self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            self.status.setText("Failed to read frame")
            return

        self.current_frame = frame
        display_frame = self.decorate_frame(frame.copy())
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = display_frame.shape
        bytes_per_line = ch * w

        image = QImage(
            display_frame.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        )
        pixmap = QPixmap.fromImage(image)

        target_size = self.camera_label.contentsRect().size()
        if target_size.width() <= 0 or target_size.height() <= 0:
            target_size = self.camera_label.size()

        scaled = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.camera_label.setPixmap(scaled)
        self.process_frame(frame)

    def decorate_frame(self, frame):
        h, w = frame.shape[:2]
        pad_x = int(w * 0.18)
        pad_y = int(h * 0.22)
        left = max(pad_x, 24)
        top = max(pad_y, 24)
        right = min(w - pad_x, w - 24)
        bottom = min(h - pad_y, h - 24)

        color = (22, 163, 74)
        thickness = 4
        corner = max(28, min((right - left) // 6, (bottom - top) // 6))

        cv2.line(frame, (left, top), (left + corner, top), color, thickness)
        cv2.line(frame, (left, top), (left, top + corner), color, thickness)

        cv2.line(frame, (right, top), (right - corner, top), color, thickness)
        cv2.line(frame, (right, top), (right, top + corner), color, thickness)

        cv2.line(frame, (left, bottom), (left + corner, bottom), color, thickness)
        cv2.line(frame, (left, bottom), (left, bottom - corner), color, thickness)

        cv2.line(frame, (right, bottom), (right - corner, bottom), color, thickness)
        cv2.line(frame, (right, bottom), (right, bottom - corner), color, thickness)
        return frame

    def process_frame(self, frame):
        pass

    def showEvent(self, event):
        super().showEvent(event)
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        QTimer.singleShot(100, self.start_camera)

    def hideEvent(self, event):
        self.stop_camera()
        super().hideEvent(event)


class ParcelEntryPage(QWidget):
    next_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(1200, 700)
        container.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f0fdf4
                );
                border-radius: 30px;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(80, 80, 80, 80)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Enter Parcel Number")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_MAIN};")

        subtitle = QLabel("Type the parcel number manually before taking a picture of the student ID")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet(f"color: {TEXT_SUB};")

        self.parcel_input = QLineEdit()
        self.parcel_input.setPlaceholderText("Parcel number")
        self.parcel_input.setMaxLength(128)
        self.parcel_input.setFixedHeight(64)
        self.parcel_input.setFont(QFont("Arial", 20))
        self.parcel_input.setStyleSheet(
            """
            QLineEdit {
                background: white;
                border: 2px solid #86efac;
                border-radius: 16px;
                padding: 0 20px;
                color: #052e16;
            }
            """
        )
        self.parcel_input.returnPressed.connect(self.handle_next)

        self.status = QLabel("Enter the parcel number to continue")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Arial", 15))
        self.status.setStyleSheet(
            f"""
            background: #bbf7d0;
            color: {PRIMARY_DARK};
            border-radius: 16px;
            padding: 10px 20px;
            """
        )

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons.setSpacing(16)

        next_btn = QPushButton("Next")
        next_btn.setFixedSize(220, 55)
        next_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_DARK};
            }}
            """
        )
        next_btn.clicked.connect(self.handle_next)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(180, 55)
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
            }
            """
        )
        cancel_btn.clicked.connect(self.cancel_requested.emit)

        buttons.addWidget(next_btn)
        buttons.addWidget(cancel_btn)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.parcel_input)
        layout.addWidget(self.status)
        layout.addLayout(buttons)

        root.addWidget(container)
        self.setLayout(root)

    def handle_next(self):
        value = self.parcel_input.text().strip()
        if not value:
            self.status.setText("Parcel number is required")
            return
        self.status.setText(f"Parcel number entered: {value}")
        self.next_requested.emit(value)

    def showEvent(self, event):
        self.parcel_input.clear()
        self.status.setText("Enter the parcel number to continue")
        super().showEvent(event)
        self.parcel_input.setFocus(Qt.FocusReason.ActiveWindowFocusReason)


class OCRScanPage(ScanPage):
    def __init__(self):
        super().__init__(
            "Take Student ID Photo",
            "Place the student ID inside the guide box, then capture the photo",
            "Capture",
        )
        self.parcel_number = ""
        self.photo_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "captures")

        self.parcel_label = QLabel("")
        self.parcel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.parcel_label.setFont(QFont("Arial", 15))
        self.parcel_label.setStyleSheet(f"color: {TEXT_MAIN}; font-weight: bold;")
        self.layout().itemAt(0).widget().layout().insertWidget(3, self.parcel_label)

    def showEvent(self, event):
        self.reset_scan_state("Live camera preview")
        self.parcel_label.setText(f"Saving photo as parcel ID: {self.parcel_number or '-'}")
        super().showEvent(event)

    def process_frame(self, frame):
        return

    def set_parcel_number(self, parcel_number):
        self.parcel_number = parcel_number

    def sanitize_parcel_number(self):
        cleaned = "".join(ch for ch in self.parcel_number.strip() if ch.isalnum() or ch in ("-", "_"))
        return cleaned or "parcel"

    def handle_next(self):
        if self.current_frame is None:
            self.status.setText("Camera frame not available")
            return

        os.makedirs(self.photo_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.sanitize_parcel_number()}_{timestamp}.jpg"
        output_path = os.path.join(self.photo_dir, filename)
        if not cv2.imwrite(output_path, self.current_frame):
            self.status.setText("Failed to save photo")
            return

        self.detected_value = output_path
        self.status.setText(f"Photo saved: {filename}")
        self.next_requested.emit(output_path)


class HomePage(QWidget):
    start_requested = pyqtSignal()
    admin_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(1200, 700)
        container.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f0fdf4
                );
                border-radius: 30px;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        logo = build_logo_label()

        title = QLabel("Parcel Collection Kiosk")
        title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_MAIN};")

        subtitle = QLabel("Enter parcel number first, then take a picture of the student ID")
        subtitle.setFont(QFont("Arial", 16))
        subtitle.setStyleSheet(f"color: {TEXT_SUB};")

        note = QLabel("Parcel number is entered manually. Student ID photo is saved using the parcel ID.")
        note.setFont(QFont("Arial", 13))
        note.setStyleSheet(f"color: {TEXT_SUB};")

        start_btn = QPushButton("Start")
        start_btn.setFixedSize(260, 70)
        start_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border-radius: 18px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {PRIMARY_DARK};
            }}
            """
        )
        start_btn.clicked.connect(self.start_requested.emit)

        admin_btn = QPushButton("Admin Login")
        admin_btn.setFixedSize(260, 60)
        admin_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                color: #052e16;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #bbf7d0;
            }
            QPushButton:hover {
                background: #f0fdf4;
            }
            """
        )
        admin_btn.clicked.connect(self.admin_requested.emit)

        layout.addWidget(logo, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(admin_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addWidget(container)
        self.setLayout(root)


class AdminLoginPage(QWidget):
    login_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(720, 420)
        container.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f0fdf4
                );
                border-radius: 30px;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Admin Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_MAIN};")

        subtitle = QLabel("Enter the admin password to view parcel logs")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Arial", 14))
        subtitle.setStyleSheet(f"color: {TEXT_SUB};")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Admin password")
        self.password_input.setFixedHeight(58)
        self.password_input.setFont(QFont("Arial", 18))
        self.password_input.setStyleSheet(
            """
            QLineEdit {
                background: white;
                border: 2px solid #86efac;
                border-radius: 16px;
                padding: 0 18px;
                color: #052e16;
            }
            """
        )
        self.password_input.returnPressed.connect(self.submit_login)

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Arial", 14))
        self.status.setStyleSheet(f"color: {PRIMARY_DARK};")

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons.setSpacing(16)

        login_btn = QPushButton("Login")
        login_btn.setFixedSize(220, 55)
        login_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_DARK};
            }}
            """
        )
        login_btn.clicked.connect(self.submit_login)

        cancel_btn = QPushButton("Back")
        cancel_btn.setFixedSize(180, 55)
        cancel_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
            }
            """
        )
        cancel_btn.clicked.connect(self.cancel_requested.emit)

        buttons.addWidget(login_btn)
        buttons.addWidget(cancel_btn)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(self.password_input)
        layout.addWidget(self.status)
        layout.addLayout(buttons)

        root.addWidget(container)
        self.setLayout(root)

    def submit_login(self):
        self.login_requested.emit(self.password_input.text())

    def showEvent(self, event):
        self.password_input.clear()
        self.status.setText("")
        super().showEvent(event)
        self.password_input.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def show_error(self, message):
        self.status.setText(message)


class AdminLogPage(QWidget):
    back_requested = pyqtSignal()
    home_requested = pyqtSignal()

    def __init__(self, workbook):
        super().__init__()
        self.workbook = workbook
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(1280, 760)
        container.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f0fdf4
                );
                border-radius: 30px;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(18)

        title = QLabel("Parcel Log")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_MAIN};")

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setFont(QFont("Arial", 14))
        self.status.setStyleSheet(f"color: {TEXT_SUB};")

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(ParcelWorkbook.HEADERS)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            """
            QTableWidget {
                background: white;
                border-radius: 18px;
                gridline-color: #dcfce7;
                color: #052e16;
            }
            QHeaderView::section {
                background: #bbf7d0;
                color: #166534;
                font-weight: bold;
                border: none;
                padding: 10px;
            }
            """
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons.setSpacing(16)

        back_btn = QPushButton("Back")
        back_btn.setFixedSize(220, 55)
        back_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: #e5e7eb;
                color: {TEXT_MAIN};
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
                border: 1px solid #cbd5e1;
            }}
            QPushButton:hover {{
                background: #d1d5db;
            }}
            """
        )
        back_btn.clicked.connect(self.back_requested.emit)

        home_btn = QPushButton("Home")
        home_btn.setFixedSize(220, 55)
        home_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: {PRIMARY_DARK};
            }}
            """
        )
        home_btn.clicked.connect(self.home_requested.emit)

        buttons.addWidget(back_btn)
        buttons.addWidget(home_btn)

        layout.addWidget(title)
        layout.addWidget(self.status)
        layout.addWidget(self.table, stretch=1)
        layout.addLayout(buttons)

        root.addWidget(container)
        self.setLayout(root)

    def refresh(self):
        try:
            records = self.workbook.read_records()
        except Exception as exc:
            self.table.setRowCount(0)
            self.status.setText(f"Failed to load records: {exc}")
            return

        self.table.setRowCount(len(records))
        for row, record in enumerate(records):
            self.table.setItem(row, 0, QTableWidgetItem(str(record.get("Number", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(record.get("Parcel ID", "")))
            self.table.setItem(row, 2, QTableWidgetItem(record.get("Timestamp", "")))
            self.table.setItem(row, 3, QTableWidgetItem(record.get("Photo Directory", "")))

        self.status.setText(f"{len(records)} record(s)")

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()


class SuccessPage(QWidget):
    done_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(1200, 700)
        container.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #ffffff,
                    stop:1 #f0fdf4
                );
                border-radius: 30px;
            }
            """
        )

        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        title = QLabel("Collection Recorded")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {TEXT_MAIN};")

        self.details = QLabel("")
        self.details.setFont(QFont("Arial", 16))
        self.details.setStyleSheet(f"color: {TEXT_MAIN};")
        self.details.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn = QPushButton("Back")
        btn.setFixedSize(260, 60)
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border-radius: 18px;
                font-weight: bold;
            }}
            """
        )
        btn.clicked.connect(self.done_requested.emit)

        layout.addWidget(title)
        layout.addWidget(self.details)
        layout.addWidget(btn)

        root.addWidget(container)
        self.setLayout(root)

    def set_result(self, record):
        self.details.setText(
            f"Number: {record['number']}\n"
            f"Parcel ID: {record['parcel_id']}\n"
            f"Time: {record['timestamp']}\n"
            f"Photo: {record['photo_path']}"
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parcel Collection Kiosk")
        self.showFullScreen()

        self.workbook = ParcelWorkbook(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "parcel_records.csv")
        )
        self.parcel_number = ""
        self.photo_path = ""
        self.last_record = None

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomePage()
        self.admin_login = AdminLoginPage()
        self.admin_logs = AdminLogPage(self.workbook)
        self.scan1 = ParcelEntryPage()
        self.scan2 = OCRScanPage()
        self.success = SuccessPage()

        self.stack.addWidget(self.home)
        self.stack.addWidget(self.admin_login)
        self.stack.addWidget(self.admin_logs)
        self.stack.addWidget(self.scan1)
        self.stack.addWidget(self.scan2)
        self.stack.addWidget(self.success)

        self.home.start_requested.connect(lambda: self.stack.setCurrentWidget(self.scan1))
        self.home.admin_requested.connect(lambda: self.stack.setCurrentWidget(self.admin_login))
        self.admin_login.login_requested.connect(self.handle_admin_login)
        self.admin_login.cancel_requested.connect(self.go_home)
        self.admin_logs.back_requested.connect(lambda: self.stack.setCurrentWidget(self.admin_login))
        self.admin_logs.home_requested.connect(self.go_home)
        self.scan1.next_requested.connect(self.go_to_student_scan)
        self.scan2.next_requested.connect(self.finish_scan)
        self.scan1.cancel_requested.connect(self.go_home)
        self.scan2.cancel_requested.connect(self.go_home)
        self.success.done_requested.connect(self.go_home)

        self.setWindowTitle(self.build_title())

    def build_title(self):
        return "Parcel Collection Kiosk"

    def go_home(self):
        self.parcel_number = ""
        self.photo_path = ""
        self.last_record = None
        self.stack.setCurrentWidget(self.home)

    def go_to_student_scan(self, parcel_number):
        self.parcel_number = parcel_number
        self.scan2.set_parcel_number(parcel_number)
        self.stack.setCurrentWidget(self.scan2)

    def handle_admin_login(self, password):
        if password != ADMIN_PASSWORD:
            self.admin_login.show_error("Invalid password")
            return
        self.stack.setCurrentWidget(self.admin_logs)

    def finish_scan(self, photo_path):
        self.photo_path = photo_path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.last_record = self.workbook.append_record(self.parcel_number, self.photo_path, timestamp)
        except Exception as exc:
            self.scan2.status.setText(f"Failed to save workbook: {exc}")
            self.stack.setCurrentWidget(self.scan2)
            return
        self.success.set_result(self.last_record)
        self.stack.setCurrentWidget(self.success)

    def closeEvent(self, event):
        self.scan2.stop_camera()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
