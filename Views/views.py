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


class CreateOrdersFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        text_styles = {"justify": "left",
                       "bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        self.Presenter = p.CreateOrders(view=self)

        back_frame = tk.Frame(self, bg="#94b4d1", relief="groove", bd=3)
        back_frame.place(rely=0.05, relx=0.05, relheight=0.85, relwidth=0.9)

        frame_order = tk.LabelFrame(back_frame, frame_styles, text="Create an Order")
        frame_order.place(rely=0.03, relx=0.02, height=150, width=300)

        label_order_1 = tk.Label(frame_order, text_styles, text="Units")
        label_order_1.place(relx=0.20, rely=0.1)

        label_order_2 = tk.Label(frame_order, text_styles, text="Instrument")
        label_order_2.place(relx=0.20, rely=0.3)

        label_order_3 = tk.Label(frame_order, text_styles, text="Acknowledge")
        label_order_3.place(relx=0.20, rely=0.5)

        frame_positions = tk.LabelFrame(back_frame, frame_styles, text="Your Current Positions")
        frame_positions.place(rely=0.40, relx=0.02, height=300, width=300)

        frame_details = tk.LabelFrame(back_frame, frame_styles, text="Execution Details")
        frame_details.place(rely=0.03, relx=0.5, height=486, width=440)

        self.label_details = tk.Label(frame_details, justify="left", bg="#D5D5D5", relief="ridge", bd=2, font=("Verdana", 10))
        self.label_details.pack(expand=True, fill="both")

        self.entry_units = ttk.Entry(frame_order, width=20, cursor="xterm")
        self.entry_units.place(relx=0.5, rely=0.1)

        self.entry_instruments = ttk.Entry(frame_order, width=20,  cursor="xterm")
        self.entry_instruments.place(relx=0.5, rely=0.3)

        self.check_val = tk.BooleanVar(parent)
        check_btn = tk.Checkbutton(frame_order, variable=self.check_val, bg="#94b4d1")
        check_btn.place(relx=0.5, rely=0.5)

        btn_exec = ttk.Button(frame_order, text="Execute Trade", command=lambda: self.create_order())
        btn_exec.place(relx=0.57, rely=0.7)

        btn_position = ttk.Button(back_frame, text="Refresh Positions", command=lambda: self.refresh_positions())
        btn_position.place(relx=0.02, rely=0.35)

        self.tv_positions = ttk.Treeview(frame_positions)
        self.tv_positions.place(relheight=1, relwidth=0.995)
        self.headers = ["Instrument", "Units"]

        self.load_position_headers()
        self.load_basic_positions()

    def load_position_headers(self):
        self.tv_positions['columns'] = self.headers
        self.tv_positions["show"] = "headings"
        for header in self.headers:
            self.tv_positions.heading(header, text=header)
            self.tv_positions.column(header, width=50)

    def load_basic_positions(self):
        self.Presenter.create_positions()

    def clear_positions(self):
        self.tv_positions.delete(*self.tv_positions.get_children())

    def update_positions(self, rows):
        for row in rows:
            self.tv_positions.insert("", "end", values=row)

    def refresh_positions(self):
        self.clear_positions()
        self.load_basic_positions()

    def create_order(self):
        units = self.entry_units.get()
        instrument = self.entry_instruments.get()
        acknowledged = self.check_val.get()
        self.Presenter.execute_trade(units=units,
                                     instrument=instrument,
                                     acknowledged=acknowledged)

    def clear_entries(self):
        self.entry_units.delete(0, "end")
        self.entry_instruments.delete(0, "end")
        self.check_val.set(False)

    def display_order_info(self, text=""):
        self.label_details["text"] = text


class SecurityPricesFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        text_styles = {"bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        self.Presenter = p.SecurityPrices(view=self)

        frame_options = tk.LabelFrame(self, frame_styles, text="Create a Chart")
        frame_options.place(rely=0.05, relx=0.05, relheight=0.40, relwidth=0.30)
        frame_price = tk.LabelFrame(self, frame_styles, text="Latest Prices")
        frame_price.place(rely=0.50, relx=0.05, relheight=0.30, relwidth=0.30)
        frame_chart = tk.LabelFrame(self, frame_styles, text="Graph")
        frame_chart.place(rely=0.05, relx=0.4, relheight=0.86, relwidth=0.55)

        self.canvas_chart = tk.Canvas(frame_chart, bg="#D5D5D5")
        self.canvas_chart.pack(expand=True, fill="both")

        frame_toolbar = tk.LabelFrame(self, frame_styles, text="Toolbar Options")
        frame_toolbar.place(rely=0.82, relx=0.05, relheight=0.09, relwidth=0.30)
        self.chart_toolbar = tk.Canvas(frame_toolbar, bg="#D5D5D5")
        self.chart_toolbar.pack(expand=True, fill="both")

        self.entry_ccy1 = ttk.Entry(frame_options, width=6, cursor="xterm")
        self.entry_ccy1.place(relx=0.50, rely=0.10)
        label_ccy1 = tk.Label(frame_options, text_styles, text="Currency 1")
        label_ccy1.place(relx=0.24, rely=0.10)

        self.entry_ccy2 = ttk.Entry(frame_options, width=6, cursor="xterm")
        self.entry_ccy2.place(relx=0.50, rely=0.25)
        label_ccy2 = tk.Label(frame_options, text_styles, text="Currency 2")
        label_ccy2.place(relx=0.24, rely=0.25)

        list_period = ("INTRADAY", "DAILY", "WEEKLY")
        list_indicator = ("No Indicator", "SMA", "EMA", "RSI")

        self.period = tk.StringVar(frame_options)
        self.indicator = tk.StringVar(frame_options)

        option_menu_period = ttk.OptionMenu(frame_options, self.period, list_period[0], *list_period)
        option_menu_period.place(relx=0.5, rely=0.40)
        label_period = tk.Label(frame_options, text_styles, text="Period")
        label_period.place(relx=0.24, rely=0.40)

        option_menu_indicator = ttk.OptionMenu(frame_options, self.indicator, list_indicator[0], *list_indicator)
        option_menu_indicator.place(relx=0.5, rely=0.55)
        label_indicator = tk.Label(frame_options, text_styles, text="Indicator")
        label_indicator.place(relx=0.24, rely=0.55)

        btn_draw = ttk.Button(frame_options, text="Draw Chart", command=lambda: self.initiate_chart())
        btn_draw.place(relx=0.64, rely=0.8)

        self.tv_prices = ttk.Treeview(frame_price)
        self.headers = ["Date", "Price"]
        self.tv_prices.place(relheight=1, relwidth=1)

        self.canvas1 = None
        self.toolbar = None

        self.load_price_headers()

    def load_price_headers(self):
        self.tv_prices['columns'] = self.headers
        self.tv_prices["show"] = "headings"

        for header in self.headers:
            self.tv_prices.heading(header, text=header)
            self.tv_prices.column(header, width=50)

    def load_prices(self):
        self.Presenter.create_prices()

    def clear_prices(self):
        self.tv_prices.delete(*self.tv_prices.get_children())

    def display_prices(self, rows):
        for row in rows:
            self.tv_prices.insert("", "end", values=row)

    def initiate_chart(self):
        self.remove_existing_chart()
        period = self.period.get()
        indicator = self.indicator.get()
        ccy1 = self.entry_ccy1.get()
        ccy2 = self.entry_ccy2.get()
        self.Presenter.create_chart(period=period, indicator=indicator,
                                    currency1=ccy1, currency2=ccy2)

    def remove_existing_chart(self):
        if self.canvas1 is not None:
            self.canvas1.destroy()
        if self.toolbar is not None:
            self.toolbar.destroy()

    def draw_chart(self, data=None, indicator=None):
        figure = plt.Figure(figsize=(4, 5), facecolor="#f0f6f7", dpi=80)
        axis = figure.add_subplot(111)
        axis.tick_params(axis="x", labelsize=8)

        rsi_check = bool(indicator == "RSI")
        ti_list = {"RSI", "SMA", "EMA"}

        data.plot(kind="line", x="Date", y="Close Price", ax=axis)

        if indicator in ti_list:
            data.plot(kind="line", x="Date",
                      y="5-period {} value".format(indicator),
                      ax=axis, secondary_y=rsi_check)

        canvas = FigureCanvasTkAgg(figure, self.canvas_chart)
        self.canvas1 = canvas.get_tk_widget()
        self.canvas1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(canvas, self.chart_toolbar)

        canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)




class CurrentPositionsFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.Presenter = p.CurrentPositions(view=self)

        frame1 = tk.LabelFrame(self, frame_styles, text="All Positions")
        frame1.place(rely=0.05, relx=0.05, relheight=0.85, relwidth=0.9)

        btn_position = ttk.Button(self, text="Refresh Positions", command=lambda: self.refresh_positions())
        btn_position.place(rely=0.9, relx=0.84)

        self.tv_positions = ttk.Treeview(frame1)
        self.tv_positions.place(relheight=1, relwidth=1)
        self.headers = ["Instrument", "Units", "Average Price",
                        "Unrealised P&L", "P&L"]

        self.load_position_headers()
        self.load_positions()

    def load_position_headers(self):
        self.tv_positions['columns'] = self.headers
        self.tv_positions["show"] = "headings"
        for header in self.headers:
            self.tv_positions.heading(header, text=header)
            self.tv_positions.column(header, width=50)

    def load_positions(self):
        self.Presenter.create_positions()

    def clear_positions(self):
        self.tv_positions.delete(*self.tv_positions.get_children())

    def update_positions(self, rows):
        for row in rows:
            self.tv_positions.insert("", "end", values=row)

    def refresh_positions(self):
        self.clear_positions()
        self.load_positions()


class PositionRecFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.Presenter = p.PositionReconciliation(view=self)

        frame1 = tk.LabelFrame(self, frame_styles, text="Position Reconciliation")
        frame1.place(rely=0.10, relx=0.05, relheight=0.75, relwidth=0.9)

        btn_position = ttk.Button(self, text="Run Reconciliation", command=lambda: self.initiate_rec())
        btn_position.place(rely=0.9, relx=0.84)

        self.tv_positions = ttk.Treeview(frame1)
        self.tv_positions.place(relheight=1, relwidth=1)
        self.headers = ["Instrument", "Units",
                        "PRMS Units", "Avg Price",
                        "PRMS Avg Price", "Position Diff",
                        "Price Diff", "Commentary"]
        self.load_table_headers()

    def initiate_rec(self):
        self.Presenter.create_rec()

    def clear_table(self):
        self.tv_positions.delete(*self.tv_positions.get_children())

    def update_table(self, rows):
        for row in rows:
            self.tv_positions.insert("", "end", values=row)

    def load_table_headers(self):
        self.tv_positions['columns'] = self.headers
        self.tv_positions["show"] = "headings"
        for header in self.headers:
            self.tv_positions.heading(header, text=header)
            self.tv_positions.column(header, width=50)
