import tkinter as tk
from tkinter import ttk
from ..basepage import BasePage
from custom_objects.datatable import DataTable
from presenters import OrderPresenter


class OrderPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.presenter = OrderPresenter(
            view=self, db=app.db, oanda=app.oanda_connection
        )

        frame_order = tk.LabelFrame(self, self.frame_styles, text="Create an Order")
        frame_order.place(rely=0.03, relx=0.02, height=150, width=300)

        label_order_1 = tk.Label(frame_order, self.text_styles, text="Units")
        label_order_1.place(relx=0.20, rely=0.1)

        label_order_2 = tk.Label(frame_order, self.text_styles, text="Instrument")
        label_order_2.place(relx=0.20, rely=0.3)

        label_order_3 = tk.Label(frame_order, self.text_styles, text="Acknowledge")
        label_order_3.place(relx=0.20, rely=0.5)

        frame_positions = tk.LabelFrame(
            self, self.frame_styles, text="Your Current Positions"
        )
        frame_positions.place(rely=0.40, relx=0.02, height=300, width=300)

        frame_details = tk.LabelFrame(self, self.frame_styles, text="Execution Details")
        frame_details.place(rely=0.03, relx=0.5, height=486, width=440)

        self.label_details = tk.Label(
            frame_details,
            justify="left",
            bg="#D5D5D5",
            relief="ridge",
            bd=2,
            font=("Verdana", 10),
        )
        self.label_details.pack(expand=True, fill="both")

        self.entry_units = ttk.Entry(frame_order, width=20, cursor="xterm")
        self.entry_units.place(relx=0.5, rely=0.1)

        self.entry_instruments = ttk.Entry(frame_order, width=20, cursor="xterm")
        self.entry_instruments.place(relx=0.5, rely=0.3)

        self.check_val = tk.BooleanVar(parent)
        check_btn = tk.Checkbutton(frame_order, variable=self.check_val, bg="#94b4d1")
        check_btn.place(relx=0.5, rely=0.5)

        btn_exec = ttk.Button(
            frame_order, text="Execute Trade", command=self.create_order
        )
        btn_exec.place(relx=0.57, rely=0.7)

        btn_position = ttk.Button(
            self, text="Refresh Positions", command=self.refresh_positions
        )
        btn_position.place(relx=0.02, rely=0.35)

        self.positions_table = DataTable(frame_positions)
        self.positions_table.place(relheight=1, relwidth=0.995)
        self.refresh_positions()

    def refresh_positions(self):
        self.presenter.get_live_positions()

    def create_order(self):
        units = self.entry_units.get()
        instrument = self.entry_instruments.get()
        acknowledged = self.check_val.get()
        self.presenter.execute_trade(
            units=units, instrument=instrument, acknowledged=acknowledged
        )

    def display_positions(self, positions):
        self.positions_table.set_datatable_from_object(positions)

    def display_order_info(self, text=""):
        self.label_details["text"] = text

    def clear_entries(self):
        self.entry_units.delete(0, "end")
        self.entry_instruments.delete(0, "end")
        self.check_val.set(False)
