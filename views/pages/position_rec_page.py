import tkinter as tk
from tkinter import ttk
from ..basepage import BasePage
from custom_objects.datatable import DataTable
from presenters import PositionRecPresenter


class PositionsRecPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.presenter = PositionRecPresenter(
            view=self, db=app.db, oanda=app.oanda_connection
        )

        frame1 = tk.LabelFrame(self, self.frame_styles, text="Position Reconciliation")
        frame1.place(rely=0.10, relx=0.05, relheight=0.75, relwidth=0.9)

        btn_position = ttk.Button(
            self, text="Run Reconciliation", command=self.initiate_rec
        )
        btn_position.place(rely=0.9, relx=0.84)

        self.positions_table = DataTable(frame1, axis="both")
        self.positions_table.place(relheight=1, relwidth=1)

    def initiate_rec(self):
        self.presenter.reconcile_positions()

    def display_reconciled_positions(self, df_positions):
        self.positions_table.set_datatable_from_dataframe(df_positions)
