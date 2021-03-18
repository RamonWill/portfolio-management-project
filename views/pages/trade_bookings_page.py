import tkinter as tk
from tkinter import ttk
from ..basepage import BasePage
from custom_objects.datatable import DataTable


class TradeBookingsPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)

        frame1 = tk.LabelFrame(self, self.frame_styles, text="Manual Entry")
        frame1.place(rely=0.05, relx=0.05, relheight=0.20, relwidth=0.55)
        frame2 = tk.LabelFrame(self, self.frame_styles, text="Cancel/Uncancel Trade")
        frame2.place(rely=0.05, relx=0.60, relheight=0.20, relwidth=0.20)
        frame3 = tk.LabelFrame(self, self.frame_styles, text="All Transactions")
        frame3.place(rely=0.25, relx=0.05, relheight=0.65, relwidth=0.9)

        label_name = tk.Label(frame1, self.text_styles, text="Security Name")
        label_name.place(rely=0.05, relx=0.05)
        label_quantity = tk.Label(frame1, self.text_styles, text="Quantity")
        label_quantity.place(rely=0.3, relx=0.05)
        label_price = tk.Label(frame1, self.text_styles, text="Price")
        label_price.place(rely=0.55, relx=0.05)

        self.entry_name = ttk.Entry(frame1, width=13, cursor="xterm")
        self.entry_name.place(rely=0.05, relx=0.25)
        self.entry_quantity = ttk.Entry(frame1, width=13, cursor="xterm")
        self.entry_quantity.place(rely=0.3, relx=0.25)
        self.entry_price = ttk.Entry(frame1, width=13, cursor="xterm")
        label_id = tk.Label(frame2, self.text_styles, text="Order ID")
        self.entry_price.place(rely=0.55, relx=0.25)

        label_id.place(rely=0.05, relx=0.05)
        self.entry_id = ttk.Entry(frame2, width=7, cursor="xterm")
        self.entry_id.place(rely=0.05, relx=0.35)
        self.check_val = tk.IntVar(parent)
        cancel_btn = tk.Radiobutton(frame2, text="Uncancel",
                                    variable=self.check_val, value=0,
                                    bg="#94b4d1")
        cancel_btn.place(rely=0.3, relx=0.35)
        uncancel_btn = tk.Radiobutton(frame2, text="Cancel",
                                      variable=self.check_val, value=1,
                                      bg="#94b4d1")
        uncancel_btn.place(rely=0.5, relx=0.35)

        btn_submit1 = ttk.Button(frame1, text="Insert",
                                 command=self.add_transaction)
        btn_submit1.place(rely=0.75, relx=0.40)
        btn_submit2 = ttk.Button(frame2, text="Amend Status",
                                 command=self.change_status)
        btn_submit2.place(rely=0.70, relx=0.35)
        btn_refresh = ttk.Button(frame1, text="Refresh",
                                 command=self.refresh_transactions)
        btn_refresh.place(rely=0.75, relx=0.60)

        self.transactions_table = DataTable(frame3, axis="both")
        self.transactions_table.place(relheight=1, relwidth=1)

    def refresh_transactions(self):
        pass

    def add_transaction(self):
        pass

    def change_status(self):
        pass
