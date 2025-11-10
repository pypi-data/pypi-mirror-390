import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QFileDialog, QListWidget, QListWidgetItem, QTabWidget, QTableWidget,
    QTableWidgetItem, QComboBox, QHeaderView, QLineEdit
)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt
import os
from PyQt6.QtWidgets import QGroupBox
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .main_app import CreatePromotionFile
class EmittingStream:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, text):
        if text.strip():
            self.text_edit.append(text)

    def flush(self):
        pass
def get_version() -> str:
    now = datetime.now()+ relativedelta(months=1)
    month = f"{now.month:02d}"
    year = str(now.year)
    version_code = f"{year[-2:]}0{month}"
    return version_code

class ModernApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Promotion Import & Report Tool")
        self.setGeometry(200, 100, 1100, 750)
        self.setAcceptDrops(True)
        self.imported_files = []
        self.init_ui()
        self.apply_theme()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Import
        self.import_tab = QWidget()
        self.init_import_tab()
        self.tabs.addTab(self.import_tab, "Import Tool")

        # Tab 2: Report
        self.report_tab = QWidget()
        self.init_report_tab()
        self.tabs.addTab(self.report_tab, "📑 Report")

        # Tab 3: Data Viewer
        self.viewer_tab = QWidget()
        self.init_viewer_tab()
        self.tabs.addTab(self.viewer_tab, "📊 Data Viewer")

        # Disable tabs at start
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)

        sys.stdout = EmittingStream(self.log_box)

    # ---------------- Teb 1 ----------------

    def init_import_tab(self):
        main_layout = QHBoxLayout(self.import_tab)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ---------------- Left ----------------
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)

        grp_input = QGroupBox("ข้อมูล Input")
        grp_layout = QVBoxLayout()
        grp_layout.setSpacing(10)

        # ช่อง 1: User (readonly)
        lbl_user = QLabel("User")
        self.le_user = QLineEdit(os.getlogin())
        self.le_user.setReadOnly(True)
        self.le_user.setStyleSheet("background:#e0e0e0; color:#555;")
        grp_layout.addWidget(lbl_user)
        grp_layout.addWidget(self.le_user)

        # ช่อง 2: IP
        lbl_ip = QLabel("IP")
        self.le_ip = QLineEdit("117.113.122.109")
        grp_layout.addWidget(lbl_ip)
        grp_layout.addWidget(self.le_ip)

        # ช่อง 3: Info (dropdown)
        lbl_info = QLabel("Load Info")
        self.cb_info = QComboBox()
        self.cb_info.addItems(["True", "False"])
        self.cb_info.setFixedHeight(30)
        grp_layout.addWidget(lbl_info)
        grp_layout.addWidget(self.cb_info)

        # ช่อง 4: Version (readonly)
        lbl_version = QLabel("Version")
        self.le_version = QLineEdit(get_version())
        self.le_version.setReadOnly(True)
        self.le_version.setStyleSheet("background:#e0e0e0; color:#555;")
        grp_layout.addWidget(lbl_version)
        grp_layout.addWidget(self.le_version)

        lbl_user = QLabel("user")
        self.le_user = QLineEdit("sa")
        grp_layout.addWidget(lbl_user)
        grp_layout.addWidget(self.le_user)

        lbl_password = QLabel("password")
        self.le_password = QLineEdit("Admin2000")
        grp_layout.addWidget(lbl_password)
        grp_layout.addWidget(self.le_password)

        lbl_master = QLabel("Database")
        self.le_master = QLineEdit("master")
        grp_layout.addWidget(lbl_master)
        grp_layout.addWidget(self.le_master)

        grp_input.setLayout(grp_layout)
        grp_input.setStyleSheet("""
            QGroupBox { font-weight:bold; font-size:13px; border:1px solid #aaa; border-radius:6px; margin-top:10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding:0 5px; }
        """)
        left_layout.addWidget(grp_input)
        left_layout.addStretch()

        # ---------------- Right ----------------
        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)

        lbl_files = QLabel("📁 ไฟล์ที่ Import:")
        lbl_files.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        right_layout.addWidget(lbl_files)

        self.file_list = QListWidget()
        self.file_list.setFixedHeight(150)
        self.file_list.setStyleSheet("""
            QListWidget {border:2px dashed #aaa; border-radius:8px; background:#fafafa;}
            QListWidget::item {padding:4px;}
        """)
        right_layout.addWidget(self.file_list)

        import_btn = QPushButton("เลือกไฟล์ (Import)")
        import_btn.setFixedHeight(35)
        import_btn.setStyleSheet("""
            QPushButton {
                background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4facfe, stop:1 #00f2fe);
                color:white; border-radius:6px; font-weight:bold;
            }
            QPushButton:hover {background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #00f2fe, stop:1 #4facfe);}
        """)
        import_btn.clicked.connect(self.import_files)
        right_layout.addWidget(import_btn)

        lbl_log = QLabel("📜 Log:")
        lbl_log.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        right_layout.addWidget(lbl_log)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background:#1e1e1e; color:#00ff9d; font-family:Consolas;")
        right_layout.addWidget(self.log_box)

        self.confirm_btn = QPushButton("ยืนยัน")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.setFixedHeight(35)
        right_layout.addWidget(self.confirm_btn)
        self.confirm_btn.clicked.connect(self.confirm_action)
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 3)
    # ---------------- Teb 2 ----------------
    def init_report_tab(self):
        layout = QVBoxLayout(self.report_tab)

        lbl_summary = QLabel("สรุปผล Report From")
        lbl_summary.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        layout.addWidget(lbl_summary)

        self.table_summary = QTableWidget(1, 14)
        headers_sum = [
            "Version", "Sum Row", "Sum Error Row", "Count Sheet", "Count Sheet Error",
            "Count Sheet Success", "Count File", "Count File Error", "Count File Success",
            "Count Promotion", "Count Product", "Count Product Not Bar",
            "Count Day", "Username"
        ]
        self.table_summary.setHorizontalHeaderLabels(headers_sum)
        self.table_summary.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_summary)


        lbl_detail = QLabel("รายละเอียดไฟล์")
        lbl_detail.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        layout.addWidget(lbl_detail)

        self.table_detail = QTableWidget(0, 9)
        headers_detail = [
            "No.", "File Name", "Sheet Name", "Count Row", "Count Col",
            "Status", "Row", "Column", "Remark"
        ]
        self.table_detail.setHorizontalHeaderLabels(headers_detail)
        self.table_detail.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_detail)

    # ---------------- Teb 3 ----------------
    def init_viewer_tab(self):
        layout = QVBoxLayout(self.viewer_tab)

        lbl_select = QLabel("🔽 เลือกชุดข้อมูล")
        lbl_select.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        layout.addWidget(lbl_select)

        select_layout = QHBoxLayout()
        self.dropdown = QComboBox()
        self.dropdown.addItems(["-- เลือกข้อมูล --", "Promotion", "Product", "Error Logs"])
        self.btn_view = QPushButton("📊 แสดงตาราง")
        self.btn_view.clicked.connect(self.load_viewer_table)
        select_layout.addWidget(self.dropdown)
        select_layout.addWidget(self.btn_view)
        layout.addLayout(select_layout)

        # Search bar
        search_layout = QHBoxLayout()
        lbl_search = QLabel("🔍 ค้นหา:")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("พิมพ์เพื่อค้นหา...")
        self.search_box.textChanged.connect(self.filter_table)
        search_layout.addWidget(lbl_search)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        # Table
        self.viewer_table = QTableWidget()
        self.viewer_table.setColumnCount(5)
        self.viewer_table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Status", "Remark"])
        self.viewer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.viewer_table.setSortingEnabled(True)
        layout.addWidget(self.viewer_table)

    # ---------------- Actions ----------------
    def import_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "เลือกไฟล์", "", "Excel Files (*.xlsx *.xls);;All Files (*.*)")
        if files:
            for f in files:
                self.imported_files.append(f)
                self.file_list.addItem(QListWidgetItem(f))
            self.confirm_btn.setEnabled(True)
            print(f"📦 Files imported manually: {len(files)}")

    def confirm_action(self):
        user_os = self.le_user.text()  # os.getlogin()
        ip = self.le_ip.text()
        version = self.le_version.text()

        # ดึงค่า DB login
        db_user = self.le_user.text()
        db_password = self.le_password.text()
        db_name = self.le_master.text()
        print(f"/n{user_os} - {ip}  - {version}")
        print(f"DB Login: {db_user} / {db_password} / {db_name}")
        print("✅ ยืนยันข้อมูลสำเร็จ")
        print(f"📂 ไฟล์ทั้งหมด: {self.imported_files}")
        self.load_report_data()
        self.tabs.setTabEnabled(1, True)
        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentIndex(1)
        load_info = self.cb_info.currentText() == "True"
        app = CreatePromotionFile(version=version,load=load_info,ip=ip,USER=db_user,PASSWORD=db_password)
        app.startui(self.imported_files)
    def load_report_data(self):
        # summary
        data = [
            "v1.0", "12345", "234", "15", "2", "13", "5", "1", "4",
            "30", "400", "12", "7", "ซีซาร์"
        ]
        for i, val in enumerate(data):
            self.table_summary.setItem(0, i, QTableWidgetItem(val))
        # detail
        rows = [
            ["1", "promotion_01.xlsx", "Sheet1", "100", "15", "Success", "-", "-", ""],
            ["2", "promotion_02.xlsx", "Sheet2", "88", "12", "Error", "34", "B", "Invalid code"],
        ]
        self.table_detail.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.table_detail.setItem(r, c, QTableWidgetItem(val))
        print("📊 Report loaded successfully.")

    def load_viewer_table(self):
        choice = self.dropdown.currentText()
        self.viewer_table.setRowCount(0)
        if choice == "Promotion":
            data = [
                ["P001", "Buy 1 Get 1", "Discount", "Active", "OK"],
                ["P002", "Lucky Draw", "Reward", "Expired", "Need review"]
            ]
        elif choice == "Product":
            data = [
                ["1001", "Coke", "Drink", "Active", ""],
                ["1002", "Lays", "Snack", "Inactive", "No barcode"]
            ]
        else:
            data = [
                ["E001", "Import Error", "System", "Resolved", "Column mismatch"],
                ["E002", "Validation Error", "Data", "Pending", "Invalid date"]
            ]

        self.viewer_table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                self.viewer_table.setItem(r, c, QTableWidgetItem(val))

        print(f"📋 แสดงข้อมูลจากชุด: {choice}")

    def filter_table(self, text):
        for row in range(self.viewer_table.rowCount()):
            visible = False
            for col in range(self.viewer_table.columnCount()):
                item = self.viewer_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    visible = True
                    break
            self.viewer_table.setRowHidden(row, not visible)

    def apply_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f0f3f7"))
        self.setPalette(palette)
        self.setStyleSheet("""
            QWidget {font-family:"Segoe UI"; color:#333;}
            QLineEdit {
                border:1px solid #ccc; border-radius:6px; padding:4px 8px;
                background:white;
            }
            QPushButton {
                border-radius:6px;
                background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #4facfe, stop:1 #00f2fe);
                color:white; padding:8px 12px; font-weight:bold;
            }
            QPushButton:disabled {background:#ccc; color:#777;}
        """)


def main():
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec())
