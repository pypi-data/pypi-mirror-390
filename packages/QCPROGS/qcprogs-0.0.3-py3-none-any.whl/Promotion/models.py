import os
from icecream import ic 
from enum import Enum, auto

class DBState(Enum):
    INIT = auto()
    CONNECTED = auto()
    CLOSED = auto()


class ReportDataManager:
    def __init__(self, version="", file_path="", sheet="", 
                 row_init=0, col_init=0, status="0",
                 map_bar=0, col_cut=0, row_cut=0, remark=""):
        self.RP_version = str(version)
        self.FILE_NAME = os.path.basename(file_path) if file_path else ""
        self.SHEET_NAME = sheet
        self.COU_ROW_INIT = str(row_init)
        self.COU_COL_INIT = str(col_init)
        self.STATUS = str(status)
        self.COU_MAP_BAR = str(map_bar)
        self.COU_COL_CUT = str(col_cut)
        self.COU_ROW_CUT = str(row_cut)
        self.REMARK = str(remark)

    def to_list(self):
        return [
            self.RP_version, self.FILE_NAME, self.SHEET_NAME,
            self.COU_ROW_INIT, self.COU_COL_INIT, self.STATUS,
            self.COU_MAP_BAR, self.COU_COL_CUT, self.COU_ROW_CUT, self.REMARK
        ]

    def to_dict(self):
        return self.__dict__.copy()

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, str(v))
        ic("Updated fields:", kwargs)

    def show(self):
        ic(self.to_dict())