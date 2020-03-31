import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path
import webbrowser
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
import matplotlib.pyplot as plt

PARENT_PATH = Path(__file__).parent.parent
sys.path.insert(0, str(PARENT_PATH))

from Presenters import presenters as p

frame_styles = {"relief": "groove",
                "bd": 3, "bg": "#94b4d1",
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}


class BaseFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        main_frame = tk.Frame(self, bg="#94b4d1", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")


class HomePageFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.Presenter = p.HomePage(view=self)

        frame_account = tk.LabelFrame(self, frame_styles, text="Account Details")
        frame_account.place(rely=0.05, relx=0.02, height=120, width=300)

        frame_prices = tk.LabelFrame(self, frame_styles, text="Tradable Securities")
        frame_prices.place(rely=0.30, relx=0.02, height=375, width=400)

        frame_news = tk.LabelFrame(self, frame_styles, text="Latest News Headlines")
        frame_news.place(rely=0.05, relx=0.45, height=280, width=550)

        frame_rec = tk.LabelFrame(self, frame_styles, text="Reconciliations at a Glance")
        frame_rec.place(rely=0.55, relx=0.80, height=222, width=190)

        frame_chart = tk.LabelFrame(self, frame_styles, text="Positions at a Glance")
        frame_chart.place(rely=0.55, relx=0.45, height=222, width=350)

        refresh_btn = ttk.Button(self, text="Refresh data", command=lambda: self.refresh_all())
        refresh_btn.place(rely=0.94, relx=0.9)

        self.label_rec_info = tk.Label(frame_rec, justify="left", bg="#D5D5D5", relief="ridge", bd=2, font=("Verdana", 10))
        self.label_rec_info.pack(expand=True, fill="both")

        self.pie_chart = tk.Canvas(frame_chart, bg="#D5D5D5", relief="solid", bd=1)
        self.pie_chart.pack()

        self.pie_canvas = None

        self.tv_account = ttk.Treeview(frame_account)
        self.tv_account.place(relheight=1, relwidth=0.995)
        self.account_headers = ["", "Information"]

        self.tv_prices = ttk.Treeview(frame_prices)
        self.tv_prices.place(relheight=1, relwidth=0.995)
        self.ts_prices = tk.Scrollbar(frame_prices)
        self.ts_prices.configure(command=self.tv_prices.yview)
        self.tv_prices.configure(yscrollcommand=self.ts_prices.set)
        self.ts_prices.pack(side="right", fill="y")
        self.price_headers = ["Instrument", "Bid Price", "Ask Price"]

        self.tv_news = ttk.Treeview(frame_news)
        self.tv_news.place(relheight=1, relwidth=0.995)
        self.news_headers = ["Top Headlines", "Source", "Link"]
        self.tv_news.bind("<Double-1>", self.Open_news_link)

        self.load_headers()
        self.load_tables()
        self.initiate_pie_chart()
        self.load_rec_summary()

    def load_headers(self):
        self.tv_account['columns'] = self.account_headers
        self.tv_account["show"] = "headings"  # removes empty column
        for header in self.account_headers:
            self.tv_account.heading(header, text=header)
            self.tv_account.column(header, width=75)

        self.tv_prices['columns'] = self.price_headers
        self.tv_prices["show"] = "headings"
        for header in self.price_headers:
            self.tv_prices.heading(header, text=header)
            self.tv_prices.column(header, width=50)

        self.tv_news['columns'] = self.news_headers
        self.tv_news["show"] = "headings"
        for header in self.news_headers:
            if header == "Top Headlines" or header == "Link":
                self.tv_news.heading(header, text=header)
                self.tv_news.column(header, width=200)
            else:
                self.tv_news.heading(header, text=header)
                self.tv_news.column(header, width=40)

    def load_rec_summary(self):
        self.Presenter.create_rec_summary()

    def update_rec_summary(self, text=""):
        self.label_rec_info["text"] = text

    def load_tables(self):
        self.Presenter.create_tables()

    def clear_tables(self):
        self.tv_account.delete(*self.tv_account.get_children())  # *=splat operator
        self.tv_prices.delete(*self.tv_prices.get_children())
        self.tv_news.delete(*self.tv_news.get_children())

    def refresh_all(self):
        self.clear_tables()
        self.load_tables()
        self.load_rec_summary()

    def update_tables(self, Tables=None):
        for row in Tables.account:
            self.tv_account.insert("", "end", values=row)
        for row in Tables.prices:
            self.tv_prices.insert("", "end", values=row)
        for row in Tables.news:
            self.tv_news.insert("", "end", values=row)

    def initiate_pie_chart(self):
        try:
            if self.pie_canvas is not None:
                self.pie_canvas.destory()
        except AttributeError:
            print("The Pie Chart is empty")
        self.Presenter.create_pie_data()

    def draw_pie_chart(self, data=None):
        if data is None:
            print("Failed to generate pie chart. Are the positions empty?")
            return None
        market_vals = data["market_values"]
        names = data["names"]

        if len(names) == 0 or len(names) == 1:
            explode = None
        else:
            explode = tuple([0.1]+[0.05]*(len(names)-1))

        colors = ["#377E9B", "#559CB9", "#7DC4E1", "#AFF6FF", "#D7FFFF"]
        fig = plt.Figure(figsize=(4, 4), facecolor="#d4d8d9")
        ax_pie = fig.add_subplot(111)
        ax_pie.pie(market_vals,
                   colors=colors,
                   explode=explode,
                   pctdistance=0.85,
                   startangle=90)
        centre_circle = plt.Circle((0, 0), 0.70, fc="#d4d8d9")
        ax_pie.add_artist(centre_circle)
        ax_pie.axis("equal")
        ax_pie.set_title("Largest Positions")
        pie_legend = ax_pie.legend(names, loc='upper left', bbox_to_anchor=(0.74, 0.35), fontsize=6)
        pie_frame = pie_legend.get_frame()
        pie_frame.set_facecolor("#babebf")
        pie_frame.set_edgecolor("#000000")
        canvas = FigureCanvasTkAgg(fig, self.pie_chart)
        self.pie_canvas = canvas.get_tk_widget()
        self.pie_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def Open_news_link(self, event):
        row_id = self.tv_news.selection()
        link = self.tv_news.item(row_id, "values")[2]
        webbrowser.open_new_tab(link)


class PositionRecFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.Presenter = p.PositionReconciliation(view=self)

        frame1 = tk.LabelFrame(self, frame_styles, text="Position Reconciliation")
        frame1.place(rely=0.10, relx=0.05, relheight=0.75, relwidth=0.9)

        button_position = ttk.Button(self, text="Run Reconciliation", command=lambda: self.initiate_rec())
        button_position.place(rely=0.9, relx=0.84)

        self.tv1 = ttk.Treeview(frame1)
        self.tv1.place(relheight=1, relwidth=1)
        self.headers = ["Instrument", "Units",
                        "PRMS Units", "Avg Price",
                        "PRMS Avg Price", "Position Diff",
                        "Price Diff", "Commentary"]
        self.load_table_headers()

    def initiate_rec(self):
        self.Presenter.create_rec()

    def clear_table(self):
        self.tv1.delete(*self.tv1.get_children())

    def update_table(self, rows):
        for row in rows:
            self.tv1.insert("", "end", values=row)

    def load_table_headers(self):
        self.tv1['columns'] = self.headers
        self.tv1["show"] = "headings"
        for header in self.headers:
            self.tv1.heading(header, text=header)
            self.tv1.column(header, width=50)
