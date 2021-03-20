import tkinter as tk
from tkinter import ttk
from ..basepage import BasePage
from custom_objects.datatable import DataTable
from presenters import PositionsPresenter


class PositionsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.presenter = PositionsPresenter(view=self, oanda=app.oanda_connection)
        frame1 = tk.LabelFrame(self, self.frame_styles, text="All Positions")
        frame1.place(rely=0.05, relx=0.05, relheight=0.85, relwidth=0.9)

        btn_position = ttk.Button(
            self, text="Refresh Positions", command=self.refresh_positions
        )
        btn_position.place(rely=0.9, relx=0.84)

        self.positions_table = DataTable(frame1, axis="x")
        self.positions_table.place(relheight=1, relwidth=1)
        self.refresh_positions()

    def refresh_positions(self):
        self.presenter.get_live_positions()

    def display_positions(self, positions):
        self.positions_table.set_datatable_from_object(positions)
