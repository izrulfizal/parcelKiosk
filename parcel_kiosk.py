import csv
import os
import sys
from datetime import datetime

import cv2
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
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

TRANSLATIONS = {
    "en": {
        "app_title": "Parcel Collection Kiosk",
        "logo_fallback": "Nilai Logo",
        "language_button": "中文",
        "home_subtitle": "Manage parcel arrival and collection from one kiosk",
        "home_note": "Arrival records start as Arrived. Collection updates them to Taken.",
        "start_collection": "Take Parcel",
        "arrival_button": "Parcel Arrived",
        "admin_login": "Admin Login",
        "enter_parcel_number": "Enter Parcel Number",
        "arrival_subtitle": "Record a parcel as arrived",
        "collection_subtitle": "Enter the parcel number before taking the student ID photo",
        "parcel_placeholder": "Parcel number",
        "enter_parcel_continue": "Enter the parcel number to continue",
        "parcel_required": "Parcel number is required",
        "parcel_entered": "Parcel number entered: {value}",
        "next": "Next",
        "save": "Save",
        "cancel": "Cancel",
        "take_student_photo": "Take Student ID Photo",
        "capture_subtitle": "Place the student ID inside the guide box, then capture the photo",
        "capture": "Capture",
        "camera_opening": "Opening camera...",
        "camera_live": "Live camera preview",
        "camera_unavailable": "Camera not available",
        "camera_failed": "Failed to read frame",
        "camera_frame_missing": "Camera frame not available",
        "camera_saved": "Photo saved: {filename}",
        "camera_save_failed": "Failed to save photo",
        "camera_saving_as": "Saving photo for parcel ID: {parcel_id}",
        "admin_login_title": "Admin Login",
        "admin_login_subtitle": "Enter the admin password to view parcel logs",
        "admin_password_placeholder": "Admin password",
        "login": "Login",
        "back": "Back",
        "home": "Home",
        "invalid_password": "Invalid password",
        "parcel_log": "Parcel Log",
        "search_placeholder": "Search parcel ID, status, timestamp, or photo path",
        "records_count": "{count} record(s)",
        "records_filtered_count": "{count} record(s) shown",
        "records_load_failed": "Failed to load records: {error}",
        "success_title": "Record Saved",
        "success_number": "Number: {value}",
        "success_parcel_id": "Parcel ID: {value}",
        "success_timestamp": "Time: {value}",
        "success_photo": "Photo: {value}",
        "success_status": "Status: {value}",
        "record_save_failed": "Failed to save records: {error}",
        "arrival_saved": "Parcel marked as arrived",
        "parcel_not_found": "No Arrived record found for parcel ID: {parcel_id}",
        "status_arrived": "Arrived",
        "status_taken": "Taken",
        "table_number": "Number",
        "table_parcel_id": "Parcel ID",
        "table_timestamp": "Timestamp",
        "table_photo_directory": "Photo Directory",
        "table_status": "Status",
        "unable_open_camera": "Unable to open camera",
        "camera_stopped": "Camera stopped",
    },
    "zh": {
        "app_title": "包裹领取系统",
        "logo_fallback": "汝来大学标志",
        "language_button": "EN",
        "home_subtitle": "在同一个系统中管理包裹到达与领取",
        "home_note": "新到包裹会记录为 Arrived，领取后会更新为 Taken。",
        "start_collection": "领取包裹",
        "arrival_button": "包裹到达",
        "admin_login": "管理员登录",
        "enter_parcel_number": "输入包裹编号",
        "arrival_subtitle": "记录包裹已到达",
        "collection_subtitle": "先输入包裹编号，再拍摄学生证照片",
        "parcel_placeholder": "包裹编号",
        "enter_parcel_continue": "请输入包裹编号以继续",
        "parcel_required": "必须输入包裹编号",
        "parcel_entered": "已输入包裹编号：{value}",
        "next": "下一步",
        "save": "保存",
        "cancel": "取消",
        "take_student_photo": "拍摄学生证照片",
        "capture_subtitle": "请将学生证放入框内，然后拍照",
        "capture": "拍照",
        "camera_opening": "正在打开相机...",
        "camera_live": "相机实时画面",
        "camera_unavailable": "相机不可用",
        "camera_failed": "读取画面失败",
        "camera_frame_missing": "没有可用的相机画面",
        "camera_saved": "照片已保存：{filename}",
        "camera_save_failed": "保存照片失败",
        "camera_saving_as": "将为包裹编号保存照片：{parcel_id}",
        "admin_login_title": "管理员登录",
        "admin_login_subtitle": "请输入管理员密码以查看包裹记录",
        "admin_password_placeholder": "管理员密码",
        "login": "登录",
        "back": "返回",
        "home": "主页",
        "invalid_password": "密码错误",
        "parcel_log": "包裹记录",
        "search_placeholder": "搜索包裹编号、状态、时间或照片路径",
        "records_count": "共 {count} 条记录",
        "records_filtered_count": "显示 {count} 条记录",
        "records_load_failed": "读取记录失败：{error}",
        "success_title": "记录已保存",
        "success_number": "编号：{value}",
        "success_parcel_id": "包裹编号：{value}",
        "success_timestamp": "时间：{value}",
        "success_photo": "照片：{value}",
        "success_status": "状态：{value}",
        "record_save_failed": "保存记录失败：{error}",
        "arrival_saved": "包裹已记录为到达",
        "parcel_not_found": "找不到该包裹的 Arrived 记录：{parcel_id}",
        "status_arrived": "Arrived",
        "status_taken": "Taken",
        "table_number": "编号",
        "table_parcel_id": "包裹编号",
        "table_timestamp": "时间",
        "table_photo_directory": "照片路径",
        "table_status": "状态",
        "unable_open_camera": "无法打开相机",
        "camera_stopped": "相机已停止",
    },
}


def build_logo_label(language, width=220, height=110):
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

    label.setText(TRANSLATIONS[language]["logo_fallback"])
    label.setStyleSheet(f"color: {TEXT_SUB};")
    return label


class ParcelRecordStore:
    HEADERS = ["Number", "Parcel ID", "Timestamp", "Photo Directory", "Status"]
    LEGACY_HEADERS = ["Number", "Parcel ID", "Timestamp", "Photo Directory"]

    def __init__(self, path):
        self.path = path

    def ensure_store(self):
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(self.HEADERS)
            return

        with open(self.path, "r", newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))

        header = rows[0] if rows else None
        if header == self.HEADERS:
            return

        if header == self.LEGACY_HEADERS:
            migrated_rows = [self.HEADERS]
            for row in rows[1:]:
                values = list(row[:4])
                while len(values) < 4:
                    values.append("")
                migrated_rows.append(values + ["Taken"])
            with open(self.path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerows(migrated_rows)
            return

        raise ValueError("Record file headers do not match expected format")

    def read_records(self):
        self.ensure_store()
        with open(self.path, "r", newline="", encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    def write_records(self, records):
        with open(self.path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self.HEADERS)
            writer.writeheader()
            writer.writerows(records)

    def append_arrival(self, parcel_id, timestamp):
        records = self.read_records()
        next_number = len(records) + 1
        record = {
            "Number": str(next_number),
            "Parcel ID": parcel_id,
            "Timestamp": timestamp,
            "Photo Directory": "",
            "Status": "Arrived",
        }
        records.append(record)
        self.write_records(records)
        return record

    def mark_taken(self, parcel_id, photo_path, timestamp):
        records = self.read_records()
        for record in reversed(records):
            if record.get("Parcel ID") == parcel_id and record.get("Status") == "Arrived":
                record["Timestamp"] = timestamp
                record["Photo Directory"] = photo_path
                record["Status"] = "Taken"
                self.write_records(records)
                return record
        raise ValueError(parcel_id)


class LanguageMixin:
    def tt(self, key, **kwargs):
        language = getattr(self, "language", "en")
        text = TRANSLATIONS[language][key]
        return text.format(**kwargs) if kwargs else text

    def bt(self, key, **kwargs):
        english = TRANSLATIONS["en"][key]
        mandarin = TRANSLATIONS["zh"][key]
        english = english.format(**kwargs) if kwargs else english
        mandarin = mandarin.format(**kwargs) if kwargs else mandarin
        return f"{english}\n{mandarin}"

    def bp(self, key, **kwargs):
        english = TRANSLATIONS["en"][key]
        mandarin = TRANSLATIONS["zh"][key]
        english = english.format(**kwargs) if kwargs else english
        mandarin = mandarin.format(**kwargs) if kwargs else mandarin
        return f"{english} / {mandarin}"


class ScanPage(QWidget, LanguageMixin):
    cancel_requested = pyqtSignal()

    def __init__(self, language="en"):
        super().__init__()
        self.language = language
        self.camera = None
        self.current_frame = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.container = QFrame()
        self.container.setFixedSize(1200, 700)
        self.container.setStyleSheet(
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

        self.layout_main = QVBoxLayout(self.container)
        self.layout_main.setContentsMargins(40, 40, 40, 40)
        self.layout_main.setSpacing(20)
        self.layout_main.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {TEXT_MAIN};")

        self.subtitle_label = QLabel()
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setFont(QFont("Arial", 14))
        self.subtitle_label.setStyleSheet(f"color: {TEXT_SUB};")
        self.subtitle_label.hide()

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

        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setWordWrap(True)
        self.camera_label.setMinimumHeight(500)
        self.camera_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)
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

        self.next_btn = QPushButton()
        self.next_btn.setFixedSize(220, 68)
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

        self.cancel_btn = QPushButton()
        self.cancel_btn.setFixedSize(180, 68)
        self.cancel_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
                color: #052e16;
            }
            """
        )
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)

        buttons.addWidget(self.next_btn)
        buttons.addWidget(self.cancel_btn)

        self.layout_main.addWidget(self.title_label)
        self.layout_main.addWidget(scan_area, stretch=1)
        self.layout_main.addLayout(buttons)

        root.addWidget(self.container)
        self.setLayout(root)

    def set_language(self, language):
        self.language = language
        self.cancel_btn.setText(self.bt("cancel"))
        self.apply_language()

    def apply_language(self):
        self.camera_label.setText(self.bt("camera_opening"))
        self.status.setText(self.bt("camera_live"))

    def handle_next(self):
        pass

    def reset_scan_state(self, message):
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
            self.camera_label.setText(self.bt("unable_open_camera"))
            self.status.setText(self.bt("camera_unavailable"))
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
        self.camera_label.setText(self.bt("camera_stopped"))

    def update_frame(self):
        if self.camera is None:
            return

        ok, frame = self.camera.read()
        if not ok:
            self.status.setText(self.bt("camera_failed"))
            return

        self.current_frame = frame
        display_frame = self.decorate_frame(frame.copy())
        display_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = display_frame.shape

        image = QImage(display_frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
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
        QTimer.singleShot(100, self.start_camera)

    def hideEvent(self, event):
        self.stop_camera()
        super().hideEvent(event)


class ParcelEntryPage(QWidget, LanguageMixin):
    submitted = pyqtSignal(str)
    cancel_requested = pyqtSignal()

    def __init__(self, mode, language="en"):
        super().__init__()
        self.mode = mode
        self.language = language
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
        layout.setContentsMargins(80, 50, 80, 80)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel()
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {TEXT_MAIN};")

        self.subtitle = QLabel()
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setFont(QFont("Arial", 14))
        self.subtitle.setStyleSheet(f"color: {TEXT_SUB};")
        self.subtitle.hide()

        self.parcel_input = QLineEdit()
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
        self.parcel_input.returnPressed.connect(self.handle_submit)

        self.status = QLabel()
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)
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

        self.submit_btn = QPushButton()
        self.submit_btn.setFixedSize(220, 68)
        self.submit_btn.setStyleSheet(
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
        self.submit_btn.clicked.connect(self.handle_submit)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setFixedSize(180, 68)
        self.cancel_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
                color: #052e16;
            }
            """
        )
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)

        buttons.addWidget(self.submit_btn)
        buttons.addWidget(self.cancel_btn)

        layout.addWidget(self.title)
        layout.addWidget(self.parcel_input)
        layout.addWidget(self.status)
        layout.addLayout(buttons)

        root.addWidget(container)
        self.setLayout(root)
        self.set_language(language)

    def set_language(self, language):
        self.language = language
        self.parcel_input.setPlaceholderText(self.bp("parcel_placeholder"))
        self.cancel_btn.setText(self.bt("cancel"))
        self.title.setText(self.bt("enter_parcel_number"))
        self.subtitle.setText(self.bt("arrival_subtitle" if self.mode == "arrival" else "collection_subtitle"))
        self.submit_btn.setText(self.bt("save" if self.mode == "arrival" else "next"))
        self.status.setText(self.bt("enter_parcel_continue"))

    def handle_submit(self):
        value = self.parcel_input.text().strip()
        if not value:
            self.status.setText(self.bt("parcel_required"))
            return
        self.status.setText(self.bt("parcel_entered", value=value))
        self.submitted.emit(value)

    def showEvent(self, event):
        self.parcel_input.clear()
        self.status.setText(self.bt("enter_parcel_continue"))
        super().showEvent(event)
        self.parcel_input.setFocus(Qt.FocusReason.ActiveWindowFocusReason)


class CapturePage(ScanPage):
    captured = pyqtSignal(str)

    def __init__(self, language="en"):
        super().__init__(language)
        self.parcel_number = ""
        self.photo_dir = os.path.join(APP_DIR, "captures")
        self.parcel_label = QLabel()
        self.parcel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.parcel_label.setWordWrap(True)
        self.parcel_label.setFont(QFont("Arial", 15))
        self.parcel_label.setStyleSheet(f"color: {TEXT_MAIN}; font-weight: bold;")
        self.layout_main.insertWidget(4, self.parcel_label)
        self.next_btn.clicked.disconnect()
        self.next_btn.clicked.connect(self.handle_next)
        self.set_language(language)

    def set_language(self, language):
        super().set_language(language)
        self.title_label.setText(self.bt("take_student_photo"))
        self.subtitle_label.setText(self.bt("capture_subtitle"))
        self.next_btn.setText(self.bt("capture"))
        self.parcel_label.setText(self.bt("camera_saving_as", parcel_id=self.parcel_number or "-"))

    def set_parcel_number(self, parcel_number):
        self.parcel_number = parcel_number
        self.parcel_label.setText(self.bt("camera_saving_as", parcel_id=self.parcel_number or "-"))

    def sanitize_parcel_number(self):
        cleaned = "".join(ch for ch in self.parcel_number.strip() if ch.isalnum() or ch in ("-", "_"))
        return cleaned or "parcel"

    def handle_next(self):
        if self.current_frame is None:
            self.status.setText(self.bt("camera_frame_missing"))
            return

        os.makedirs(self.photo_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.sanitize_parcel_number()}_{timestamp}.jpg"
        output_path = os.path.join(self.photo_dir, filename)
        if not cv2.imwrite(output_path, self.current_frame):
            self.status.setText(self.bt("camera_save_failed"))
            return

        self.status.setText(self.bt("camera_saved", filename=filename))
        self.captured.emit(output_path)

    def showEvent(self, event):
        self.reset_scan_state(self.bt("camera_live"))
        self.parcel_label.setText(self.bt("camera_saving_as", parcel_id=self.parcel_number or "-"))
        super().showEvent(event)


class HomePage(QWidget, LanguageMixin):
    collection_requested = pyqtSignal()
    arrival_requested = pyqtSignal()
    admin_requested = pyqtSignal()

    def __init__(self, language="en"):
        super().__init__()
        self.language = language
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(1200, 720)
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
        layout.setContentsMargins(50, 40, 50, 50)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self.logo_holder = QWidget()
        self.logo_layout = QVBoxLayout(self.logo_holder)
        self.logo_layout.setContentsMargins(0, 0, 0, 0)

        self.title = QLabel()
        self.title.setWordWrap(True)
        self.title.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {TEXT_MAIN};")

        self.subtitle = QLabel()
        self.subtitle.setWordWrap(True)
        self.subtitle.setFont(QFont("Arial", 16))
        self.subtitle.setStyleSheet(f"color: {TEXT_SUB};")
        self.subtitle.hide()

        self.note = QLabel()
        self.note.setWordWrap(True)
        self.note.setFont(QFont("Arial", 13))
        self.note.setStyleSheet(f"color: {TEXT_SUB};")
        self.note.hide()

        self.arrival_btn = QPushButton()
        self.arrival_btn.setFixedSize(300, 82)
        self.arrival_btn.setStyleSheet(
            """
            QPushButton {
                background: white;
                color: #052e16;
                border-radius: 18px;
                font-size: 18px;
                font-weight: bold;
                border: 2px solid #86efac;
            }
            QPushButton:hover {
                background: #f0fdf4;
            }
            """
        )
        self.arrival_btn.clicked.connect(self.arrival_requested.emit)

        self.collection_btn = QPushButton()
        self.collection_btn.setFixedSize(300, 82)
        self.collection_btn.setStyleSheet(
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
        self.collection_btn.clicked.connect(self.collection_requested.emit)

        self.admin_btn = QPushButton()
        self.admin_btn.setFixedSize(300, 74)
        self.admin_btn.setStyleSheet(
            """
            QPushButton {
                background: #e5e7eb;
                color: #052e16;
                border-radius: 18px;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #cbd5e1;
            }
            QPushButton:hover {
                background: #d1d5db;
            }
            """
        )
        self.admin_btn.clicked.connect(self.admin_requested.emit)

        layout.addWidget(self.logo_holder, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.arrival_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.collection_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.admin_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        root.addWidget(container)
        self.setLayout(root)
        self.set_language(language)

    def set_language(self, language):
        self.language = language
        self.title.setText(self.bt("app_title"))
        self.subtitle.setText(self.bt("home_subtitle"))
        self.note.setText(self.bt("home_note"))
        self.arrival_btn.setText(self.bt("arrival_button"))
        self.collection_btn.setText(self.bt("start_collection"))
        self.admin_btn.setText(self.bt("admin_login"))

        while self.logo_layout.count():
            item = self.logo_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.logo_layout.addWidget(build_logo_label(language))


class AdminLoginPage(QWidget, LanguageMixin):
    login_requested = pyqtSignal(str)
    cancel_requested = pyqtSignal()

    def __init__(self, language="en"):
        super().__init__()
        self.language = language
        self.setStyleSheet(f"background-color: {APP_BG};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container = QFrame()
        container.setFixedSize(720, 440)
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
        layout.setContentsMargins(60, 40, 60, 60)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel()
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {TEXT_MAIN};")

        self.subtitle = QLabel()
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle.setWordWrap(True)
        self.subtitle.setFont(QFont("Arial", 14))
        self.subtitle.setStyleSheet(f"color: {TEXT_SUB};")
        self.subtitle.hide()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
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

        self.login_btn = QPushButton()
        self.login_btn.setFixedSize(220, 68)
        self.login_btn.setStyleSheet(
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
        self.login_btn.clicked.connect(self.submit_login)

        self.cancel_btn = QPushButton()
        self.cancel_btn.setFixedSize(180, 68)
        self.cancel_btn.setStyleSheet(
            """
            QPushButton {
                background: #e5e7eb;
                color: #052e16;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
                border: 1px solid #cbd5e1;
            }
            QPushButton:hover {
                background: #d1d5db;
            }
            """
        )
        self.cancel_btn.clicked.connect(self.cancel_requested.emit)

        buttons.addWidget(self.login_btn)
        buttons.addWidget(self.cancel_btn)

        layout.addWidget(self.title)
        layout.addWidget(self.password_input)
        layout.addWidget(self.status)
        layout.addLayout(buttons)

        root.addWidget(container)
        self.setLayout(root)
        self.set_language(language)

    def set_language(self, language):
        self.language = language
        self.title.setText(self.bt("admin_login_title"))
        self.subtitle.setText(self.bt("admin_login_subtitle"))
        self.password_input.setPlaceholderText(self.bp("admin_password_placeholder"))
        self.login_btn.setText(self.bt("login"))
        self.cancel_btn.setText(self.bt("back"))

    def submit_login(self):
        self.login_requested.emit(self.password_input.text())

    def showEvent(self, event):
        self.password_input.clear()
        self.status.setText("")
        super().showEvent(event)
        self.password_input.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def show_error(self, message):
        self.status.setText(message)


class AdminLogPage(QWidget, LanguageMixin):
    back_requested = pyqtSignal()
    home_requested = pyqtSignal()

    def __init__(self, store, language="en"):
        super().__init__()
        self.store = store
        self.language = language
        self.records = []
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

        self.title = QLabel()
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {TEXT_MAIN};")

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setWordWrap(True)
        self.status.setFont(QFont("Arial", 14))
        self.status.setStyleSheet(f"color: {TEXT_SUB};")

        self.search_input = QLineEdit()
        self.search_input.setFixedHeight(50)
        self.search_input.setFont(QFont("Arial", 15))
        self.search_input.setStyleSheet(
            """
            QLineEdit {
                background: white;
                border: 2px solid #bbf7d0;
                border-radius: 14px;
                padding: 0 16px;
                color: #052e16;
            }
            """
        )
        self.search_input.textChanged.connect(self.apply_filter)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
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
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        buttons = QHBoxLayout()
        buttons.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons.setSpacing(16)

        self.back_btn = QPushButton()
        self.back_btn.setFixedSize(220, 68)
        self.back_btn.setStyleSheet(
            """
            QPushButton {
                background: #e5e7eb;
                color: #052e16;
                border-radius: 16px;
                font-weight: bold;
                font-size: 15px;
                border: 1px solid #cbd5e1;
            }
            QPushButton:hover {
                background: #d1d5db;
            }
            """
        )
        self.back_btn.clicked.connect(self.back_requested.emit)

        self.home_btn = QPushButton()
        self.home_btn.setFixedSize(220, 68)
        self.home_btn.setStyleSheet(
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
        self.home_btn.clicked.connect(self.home_requested.emit)

        buttons.addWidget(self.back_btn)
        buttons.addWidget(self.home_btn)

        layout.addWidget(self.title)
        layout.addWidget(self.status)
        layout.addWidget(self.search_input)
        layout.addWidget(self.table, stretch=1)
        layout.addLayout(buttons)

        root.addWidget(container)
        self.setLayout(root)
        self.set_language(language)

    def set_language(self, language):
        self.language = language
        self.title.setText(self.bt("parcel_log"))
        self.back_btn.setText(self.bt("back"))
        self.home_btn.setText(self.bt("home"))
        self.search_input.setPlaceholderText(self.bp("search_placeholder"))
        self.table.setHorizontalHeaderLabels(
            [
                self.bt("table_number"),
                self.bt("table_parcel_id"),
                self.bt("table_timestamp"),
                self.bt("table_photo_directory"),
                self.bt("table_status"),
            ]
        )
        self.refresh()

    def refresh(self):
        try:
            self.records = self.store.read_records()
        except Exception as exc:
            self.table.setRowCount(0)
            self.status.setText(self.bt("records_load_failed", error=exc))
            return

        self.apply_filter()

    def apply_filter(self):
        query = self.search_input.text().strip().lower()
        if query:
            filtered_records = [
                record
                for record in self.records
                if query in " ".join(
                    [
                        record.get("Number", ""),
                        record.get("Parcel ID", ""),
                        record.get("Timestamp", ""),
                        record.get("Photo Directory", ""),
                        record.get("Status", ""),
                    ]
                ).lower()
            ]
        else:
            filtered_records = list(self.records)

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(filtered_records))
        for row, record in enumerate(filtered_records):
            self.table.setItem(row, 0, QTableWidgetItem(record.get("Number", "")))
            self.table.setItem(row, 1, QTableWidgetItem(record.get("Parcel ID", "")))
            self.table.setItem(row, 2, QTableWidgetItem(record.get("Timestamp", "")))
            self.table.setItem(row, 3, QTableWidgetItem(record.get("Photo Directory", "")))
            self.table.setItem(row, 4, QTableWidgetItem(record.get("Status", "")))
        self.table.setSortingEnabled(True)

        status_key = "records_filtered_count" if query else "records_count"
        self.status.setText(self.bt(status_key, count=len(filtered_records)))

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()


class SuccessPage(QWidget, LanguageMixin):
    done_requested = pyqtSignal()

    def __init__(self, language="en"):
        super().__init__()
        self.language = language
        self.record = None
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
        layout.setContentsMargins(60, 40, 60, 60)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(18)

        self.title = QLabel()
        self.title.setWordWrap(True)
        self.title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        self.title.setStyleSheet(f"color: {TEXT_MAIN};")

        self.details = QLabel("")
        self.details.setFont(QFont("Arial", 16))
        self.details.setStyleSheet(f"color: {TEXT_MAIN};")
        self.details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.details.setWordWrap(True)

        self.done_btn = QPushButton()
        self.done_btn.setFixedSize(260, 74)
        self.done_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {PRIMARY};
                color: white;
                border-radius: 18px;
                font-weight: bold;
            }}
            """
        )
        self.done_btn.clicked.connect(self.done_requested.emit)

        layout.addWidget(self.title)
        layout.addWidget(self.details)
        layout.addWidget(self.done_btn)

        root.addWidget(container)
        self.setLayout(root)
        self.set_language(language)

    def set_language(self, language):
        self.language = language
        self.title.setText(self.bt("success_title"))
        self.done_btn.setText(self.bt("home"))
        if self.record:
            self.set_record(self.record)

    def set_record(self, record):
        self.record = record
        photo_value = record.get("Photo Directory", "") or "-"
        self.details.setText(
            "\n".join(
                [
                    self.bt("success_number", value=record.get("Number", "-")),
                    self.bt("success_parcel_id", value=record.get("Parcel ID", "-")),
                    self.bt("success_timestamp", value=record.get("Timestamp", "-")),
                    self.bt("success_status", value=record.get("Status", "-")),
                    self.bt("success_photo", value=photo_value),
                ]
            )
        )


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.language = "en"
        self.setWindowTitle(TRANSLATIONS[self.language]["app_title"])
        self.showFullScreen()

        self.store = ParcelRecordStore(os.path.join(APP_DIR, "parcel_records.csv"))
        self.parcel_number = ""
        self.photo_path = ""

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomePage(self.language)
        self.admin_login = AdminLoginPage(self.language)
        self.admin_logs = AdminLogPage(self.store, self.language)
        self.arrival_page = ParcelEntryPage("arrival", self.language)
        self.collection_page = ParcelEntryPage("collection", self.language)
        self.capture_page = CapturePage(self.language)
        self.success_page = SuccessPage(self.language)

        for page in [
            self.home,
            self.admin_login,
            self.admin_logs,
            self.arrival_page,
            self.collection_page,
            self.capture_page,
            self.success_page,
        ]:
            self.stack.addWidget(page)

        self.home.collection_requested.connect(lambda: self.stack.setCurrentWidget(self.collection_page))
        self.home.arrival_requested.connect(lambda: self.stack.setCurrentWidget(self.arrival_page))
        self.home.admin_requested.connect(lambda: self.stack.setCurrentWidget(self.admin_login))

        self.arrival_page.submitted.connect(self.record_arrival)
        self.collection_page.submitted.connect(self.go_to_capture)
        self.capture_page.captured.connect(self.finish_collection)

        self.admin_login.login_requested.connect(self.handle_admin_login)
        self.admin_login.cancel_requested.connect(self.go_home)
        self.admin_logs.back_requested.connect(lambda: self.stack.setCurrentWidget(self.admin_login))
        self.admin_logs.home_requested.connect(self.go_home)

        self.arrival_page.cancel_requested.connect(self.go_home)
        self.collection_page.cancel_requested.connect(self.go_home)
        self.capture_page.cancel_requested.connect(self.go_home)
        self.success_page.done_requested.connect(self.go_home)

    def go_home(self):
        self.parcel_number = ""
        self.photo_path = ""
        self.stack.setCurrentWidget(self.home)

    def record_arrival(self, parcel_number):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            record = self.store.append_arrival(parcel_number, timestamp)
        except Exception as exc:
            self.arrival_page.status.setText(self.arrival_page.bt("record_save_failed", error=exc))
            return
        self.success_page.set_record(record)
        self.stack.setCurrentWidget(self.success_page)

    def go_to_capture(self, parcel_number):
        self.parcel_number = parcel_number
        self.capture_page.set_parcel_number(parcel_number)
        self.stack.setCurrentWidget(self.capture_page)

    def handle_admin_login(self, password):
        if password != ADMIN_PASSWORD:
            self.admin_login.show_error(self.admin_login.bt("invalid_password"))
            return
        self.stack.setCurrentWidget(self.admin_logs)

    def finish_collection(self, photo_path):
        self.photo_path = photo_path
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            record = self.store.mark_taken(self.parcel_number, self.photo_path, timestamp)
        except ValueError:
            self.collection_page.status.setText(
                self.collection_page.bt("parcel_not_found", parcel_id=self.parcel_number)
            )
            self.stack.setCurrentWidget(self.collection_page)
            return
        except Exception as exc:
            self.capture_page.status.setText(self.capture_page.bt("record_save_failed", error=exc))
            return

        self.success_page.set_record(record)
        self.stack.setCurrentWidget(self.success_page)

    def closeEvent(self, event):
        self.capture_page.stop_camera()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
