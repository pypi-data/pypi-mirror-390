import sys, os
sys.path.append(os.path.dirname(__file__)) 
import flet as ft
from UI import DataUI
def main(page: ft.Page):
    ui = DataUI(page)
    page.title = "Data Query UI"
    page.add(ui.build())
def start():
    ft.app(target=main)
    
if __name__ == '__main__':
    start()