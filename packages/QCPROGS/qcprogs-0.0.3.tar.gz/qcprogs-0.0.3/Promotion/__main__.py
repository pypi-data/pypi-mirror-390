from .main_app import CreatePromotionFile
from .utils import check_and_install_fonts,get_version,font_list
from PyQt6.QtWidgets import   QApplication
import sys
from .ui import ModernApp
def main_app():
    try:
        check_and_install_fonts(font_list)
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการติดตั้งฟอนต์: {e}")
    CreatePromotion = CreatePromotionFile(load=True,sub_sheet=True)
    version :str = get_version()
    CreatePromotion._set_version(version)
    CreatePromotion.start()

def UI_app():
    app = QApplication(sys.argv)
    window = ModernApp()
    window.show()
    sys.exit(app.exec())





if __name__ == "__main__":
    main_app()
