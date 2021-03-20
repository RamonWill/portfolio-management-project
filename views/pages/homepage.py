import tkinter as tk
from tkinter import ttk
import webbrowser
from ..basepage import BasePage
from presenters import HomePresenter
from custom_objects.datatable import DataTable
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


class HomePage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.presenter = HomePresenter(
            view=self, db=app.db, news=app.news_connection, oanda=app.oanda_connection
        )

        frame_account = tk.LabelFrame(self, self.frame_styles, text="Account Details")
        frame_account.place(rely=0.05, relx=0.02, height=120, width=300)

        frame_prices = tk.LabelFrame(
            self, self.frame_styles, text="Tradable Securities"
        )
        frame_prices.place(rely=0.30, relx=0.02, height=375, width=400)

        frame_news = tk.LabelFrame(
            self, self.frame_styles, text="Latest News Headlines"
        )
        frame_news.place(rely=0.05, relx=0.45, height=280, width=550)

        frame_rec = tk.LabelFrame(
            self, self.frame_styles, text="Reconciliations at a Glance"
        )
        frame_rec.place(rely=0.55, relx=0.80, height=222, width=190)

        frame_chart = tk.LabelFrame(
            self, self.frame_styles, text="Positions at a Glance"
        )
        frame_chart.place(rely=0.55, relx=0.45, height=222, width=350)

        refresh_btn = ttk.Button(self, text="Refresh data", command=self._refresh_all)
        refresh_btn.place(rely=0.94, relx=0.9)

        self.label_rec_info = tk.Label(
            frame_rec,
            justify="left",
            bg="#D5D5D5",
            relief="ridge",
            bd=2,
            font=("Verdana", 10),
        )
        self.label_rec_info.pack(expand=True, fill="both")

        self.news_table = DataTable(frame_news, axis="both")
        self.news_table.place(relheight=1, relwidth=0.995)
        self.news_table.bind("<Double-1>", self.open_news_link)
        self.prices_table = DataTable(frame_prices, axis="both")
        self.prices_table.place(relheight=1, relwidth=0.995)
        self.account_table = DataTable(frame_account, axis="x")
        self.account_table.place(relheight=1, relwidth=0.995)

        self.pie_chart = tk.Canvas(frame_chart, bg="#D5D5D5", relief="solid", bd=1)
        self.pie_chart.pack()

        self.pie_canvas = None
        self._refresh_all()

    def _refresh_all(self):
        self.presenter.get_homepage_data()
        self.initiate_pie_chart()

    def open_news_link(self, event):
        row_id = self.news_table.selection()
        link = self.news_table.item(row_id, "values")[2]
        webbrowser.open_new_tab(link)

    def display_data(self, articles, account_summary, securities):
        self.news_table.set_datatable_from_object(articles)
        self.account_table.set_datatable_from_object(account_summary)
        self.prices_table.set_datatable_from_object(securities)

    def display_rec_status(self, status):
        self.label_rec_info["text"] = status

    def initiate_pie_chart(self):
        try:
            if self.pie_canvas is not None:
                self.pie_canvas.destory()
        except AttributeError:
            print("The Pie Chart is empty")
        self.presenter.create_pie_data()

    def draw_pie_chart(self, data=None):
        if data.empty:
            print("Failed to generate pie chart. Are the positions empty?")
            return None
        market_vals = data["MarketVal"]
        names = data["name"]

        if len(names) == 0 or len(names) == 1:
            explode = None
        else:
            explode = tuple([0.1] + [0.05] * (len(names) - 1))

        colors = ["#377E9B", "#559CB9", "#7DC4E1", "#AFF6FF", "#D7FFFF"]
        fig = plt.Figure(figsize=(4, 4), facecolor="#d4d8d9")
        ax_pie = fig.add_subplot(111)
        ax_pie.pie(
            market_vals, colors=colors, explode=explode, pctdistance=0.85, startangle=90
        )
        centre_circle = plt.Circle((0, 0), 0.70, fc="#d4d8d9")
        ax_pie.add_artist(centre_circle)
        ax_pie.axis("equal")
        ax_pie.set_title("Largest Positions")
        pie_legend = ax_pie.legend(
            names, loc="upper left", bbox_to_anchor=(0.74, 0.35), fontsize=6
        )
        pie_frame = pie_legend.get_frame()
        pie_frame.set_facecolor("#babebf")
        pie_frame.set_edgecolor("#000000")
        canvas = FigureCanvasTkAgg(fig, self.pie_chart)
        self.pie_canvas = canvas.get_tk_widget()
        self.pie_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
