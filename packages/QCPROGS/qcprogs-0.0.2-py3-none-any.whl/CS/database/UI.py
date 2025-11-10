import sys, os
sys.path.append(os.path.dirname(__file__)) 
import flet as ft
import pandas as pd
from config import ALL_TABEL_MAPPING
from database import OracleDB
from icecream import ic

class DataUI:
    PAGE_SIZE = 20
    CONFIG = [v.get("TABEL") for v in ALL_TABEL_MAPPING if v.get("TABEL")]

    def __init__(self, page: ft.Page):
        self.page = page

        # Controls
        self.dd_code = ft.TextField(label="CS CODE")
        self.dd_vendor = ft.TextField(label="VENDOR CODE")
        self.dd_service = ft.TextField(label="SERVICE ID")

        self.db_config = {
            "ONLPRD_19C": {"HOST": "csonldbuat-scan.counterservice.co.th", "PORT": "1521"},
            "ONLPRD_12C": {"HOST": "csonldbqa01.counterservice.co.th", "PORT": "1521"}
        }

        self.dd_database = ft.Dropdown(
            label="DATABASE",
            options=[ft.dropdown.Option(k) for k in self.db_config.keys()],
            on_change=self.on_database_change
        )

        self.txt_host = ft.TextField(label="HOST", disabled=True)
        self.txt_port = ft.TextField(label="PORT", disabled=True)

        self.dd_TABEL = ft.Dropdown(
            label="TABLE",
            options=[ft.dropdown.Option(k) for k in self.CONFIG],
            value=self.CONFIG[0]
        )

        self.btn_search = ft.ElevatedButton(text="Search", on_click=self.on_search)
        self.btn_export = ft.ElevatedButton(text="Export", disabled=True, on_click=self.on_export)

        self.result_controls = ft.Column()
        self.btn_prev = ft.ElevatedButton("<< Previous", on_click=self.prev_page)
        self.btn_next = ft.ElevatedButton("Next >>", on_click=self.next_page)
        self.pagination_row = ft.Row([self.btn_prev, self.btn_next], alignment=ft.MainAxisAlignment.CENTER)

        # Data
        self.data_result = None
        self.rows = []
        self.columns = []
        self.current_page = 0
        self.total_pages = 0

        # Oracle handler
        self.funtion = OracleDB("csonldbqa01.counterservice.co.th") # type: ignore

    # --- Event Handlers ---
    def on_database_change(self, e):
        db_info = self.db_config.get(self.dd_database.value, {"HOST": "", "PORT": ""}) # type: ignore
        self.txt_host.value = db_info["HOST"]
        self.txt_port.value = db_info["PORT"]
        self.txt_host.update()
        self.txt_port.update()

    def on_search(self, e):
        cs = str(self.dd_code.value).strip()
        vd = str(self.dd_vendor.value).strip()
        sv = str(self.dd_service.value).strip()
        ul = str(self.txt_host.value).strip()
        tb = str(self.dd_TABEL.value).strip()
        ic([cs,vd,sv,ul,tb])
        if not cs !='' and not vd !='':
            ic('step : 1')
            self.page.snack_bar = ft.SnackBar(ft.Text("กรุณากรอก CS CODE หรือ VENDOR CODE"), open=True) # type: ignore
            self.page.update()
            return

        try:
            ic('step : 2')
            self.funtion._set_url(ul)
            data_result = self.funtion.fetch_tables( cs_code=cs, values= vd,service= sv, include=[tb])
            if not data_result:
                ic('step : 3')
                self.result_controls.controls.clear()
                self.result_controls.controls.append(ft.Text("ไม่พบข้อมูล"))
                self.btn_export.disabled = True
                self.page.update()
                return
            ic('step : 4')
            columns = data_result.get("Column", [])
            rows = data_result.get("Row", [])
            self.rows =[row[:9] for row in rows]
            self.columns =columns[:9]
            ic(self.columns, self.rows )
            self.current_page = 0
            self.total_pages = (len(self.rows) + self.PAGE_SIZE - 1) // self.PAGE_SIZE
            self.btn_export.disabled = False
            self.refresh_table()

        except Exception as ex:
            ic(f'step : {ex}')
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {ex}"), open=True) # type: ignore
            self.page.update()

    def on_export(self, e):
        cs = str(self.dd_code.value).strip()
        vd = str(self.dd_vendor.value).strip()
        sv = str(self.dd_service.value).strip()
        self.funtion.export_file(vd,cs,sv)

    # --- Pagination ---
    def next_page(self, e):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.refresh_table()

    def prev_page(self, e):
        if self.current_page > 0:
            self.current_page -= 1
            self.refresh_table()

    def refresh_table(self):
        self.result_controls.controls.clear()
        self.result_controls.controls.append(self.build_table_page())
        self.btn_prev.disabled = self.current_page == 0
        self.btn_next.disabled = self.current_page >= self.total_pages - 1
        self.result_controls.controls.append(self.pagination_row)
        self.page.update()

        # --- Table Builder ---
    def build_table_page(self):
        start_idx = self.current_page * self.PAGE_SIZE
        end_idx = start_idx + self.PAGE_SIZE
        page_rows = self.rows[start_idx:end_idx]

        data_columns = [ft.DataColumn(ft.Text(col)) for col in self.columns]
        data_rows = []
        for row in page_rows:
            safe_row = list(row) + [""] * (len(self.columns) - len(row))
            cells = [ft.DataCell(ft.Text(str(val))) for val in safe_row]
            data_rows.append(ft.DataRow(cells=cells))

        table = ft.DataTable(
            columns=data_columns,
            rows=data_rows,
            border=ft.border.all(1),
            vertical_lines=ft.border.all(0.5), # type: ignore
            data_row_min_height=30,
            column_spacing=8
        )
        return table

    # --- Build UI ---
    def build(self):
        return ft.Column([
            ft.Row([self.dd_code, self.dd_vendor, self.dd_service, self.dd_database]),
            ft.Row([self.txt_host, self.txt_port, self.dd_TABEL, self.btn_search, self.btn_export]),
            ft.Divider(),
            ft.Container(ft.ListView(
                controls=[self.result_controls],
                width=1000,
                height=400,
                on_scroll=ft.ScrollMode.ALWAYS))]) # type: ignore



def main(page: ft.Page):
    ui = DataUI(page)
    page.title = "Data Query UI"
    page.add(ui.build())


if __name__ == "__main__":
    ft.app(target=main)
