import tkinter as tk
from tkinter import ttk
import webbrowser
from ..basepage import BasePage
from custom_objects.datatable import DataTable


class HomePage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)
        frame_account = tk.LabelFrame(self, self.frame_styles,
                                      text="Account Details")
        frame_account.place(rely=0.05, relx=0.02, height=120, width=300)

        frame_prices = tk.LabelFrame(self, self.frame_styles,
                                     text="Tradable Securities")
        frame_prices.place(rely=0.30, relx=0.02, height=375, width=400)

        frame_news = tk.LabelFrame(self, self.frame_styles,
                                   text="Latest News Headlines")
        frame_news.place(rely=0.05, relx=0.45, height=280, width=550)

        frame_rec = tk.LabelFrame(self, self.frame_styles,
                                  text="Reconciliations at a Glance")
        frame_rec.place(rely=0.55, relx=0.80, height=222, width=190)

        frame_chart = tk.LabelFrame(self, self.frame_styles,
                                    text="Positions at a Glance")
        frame_chart.place(rely=0.55, relx=0.45, height=222, width=350)

        refresh_btn = ttk.Button(self, text="Refresh data",
                                 command=lambda: self.refresh_all())
        refresh_btn.place(rely=0.94, relx=0.9)

        self.label_rec_info = tk.Label(frame_rec, justify="left",
                                       bg="#D5D5D5", relief="ridge",
                                       bd=2, font=("Verdana", 10))
        self.label_rec_info.pack(expand=True, fill="both")

        self.news_table = DataTable(frame_news)
        self.news_table.place(relheight=1, relwidth=0.995)
        self.news_table.bind("<Double-1>", self.open_news_link)
        self.prices_table = DataTable(frame_prices, is_scrollable=True)
        self.prices_table.place(relheight=1, relwidth=0.995)
        self.account_table = DataTable(frame_account)
        self.account_table.place(relheight=1, relwidth=0.995)

        self.pie_chart = tk.Canvas(frame_chart, bg="#D5D5D5",
                                   relief="solid", bd=1)
        self.pie_chart.pack()

        self.pie_canvas = None


    def _refresh_all(self):
        pass

    def open_news_link(self, event):
        row_id = self.tv_news.selection()
        link = self.tv_news.item(row_id, "values")[2]
        webbrowser.open_new_tab(link)
