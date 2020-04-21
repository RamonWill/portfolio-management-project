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
    def __init__(self, parent, app):
        super().__init__(parent)

        self.Presenter = p.HomePage(view=self)

        frame_account = tk.LabelFrame(self, frame_styles,
                                      text="Account Details")
        frame_account.place(rely=0.05, relx=0.02, height=120, width=300)

        frame_prices = tk.LabelFrame(self, frame_styles,
                                     text="Tradable Securities")
        frame_prices.place(rely=0.30, relx=0.02, height=375, width=400)

        frame_news = tk.LabelFrame(self, frame_styles,
                                   text="Latest News Headlines")
        frame_news.place(rely=0.05, relx=0.45, height=280, width=550)

        frame_rec = tk.LabelFrame(self, frame_styles,
                                  text="Reconciliations at a Glance")
        frame_rec.place(rely=0.55, relx=0.80, height=222, width=190)

        frame_chart = tk.LabelFrame(self, frame_styles,
                                    text="Positions at a Glance")
        frame_chart.place(rely=0.55, relx=0.45, height=222, width=350)

        refresh_btn = ttk.Button(self, text="Refresh data",
                                 command=lambda: self.refresh_all())
        refresh_btn.place(rely=0.94, relx=0.9)

        self.label_rec_info = tk.Label(frame_rec, justify="left",
                                       bg="#D5D5D5", relief="ridge",
                                       bd=2, font=("Verdana", 10))
        self.label_rec_info.pack(expand=True, fill="both")

        self.pie_chart = tk.Canvas(frame_chart, bg="#D5D5D5",
                                   relief="solid", bd=1)
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
        self.tv_account.delete(*self.tv_account.get_children())
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
        pie_legend = ax_pie.legend(names,
                                   loc='upper left',
                                   bbox_to_anchor=(0.74, 0.35),
                                   fontsize=6)
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
    def __init__(self, parent, app):
        super().__init__(parent)

        text_styles = {"justify": "left",
                       "bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        self.Presenter = p.CreateOrders(view=self)

        back_frame = tk.Frame(self, bg="#94b4d1", relief="groove", bd=3)
        back_frame.place(rely=0.05, relx=0.05, relheight=0.85, relwidth=0.9)

        frame_order = tk.LabelFrame(back_frame, frame_styles,
                                    text="Create an Order")
        frame_order.place(rely=0.03, relx=0.02, height=150, width=300)

        label_order_1 = tk.Label(frame_order, text_styles, text="Units")
        label_order_1.place(relx=0.20, rely=0.1)

        label_order_2 = tk.Label(frame_order, text_styles, text="Instrument")
        label_order_2.place(relx=0.20, rely=0.3)

        label_order_3 = tk.Label(frame_order, text_styles, text="Acknowledge")
        label_order_3.place(relx=0.20, rely=0.5)

        frame_positions = tk.LabelFrame(back_frame, frame_styles,
                                        text="Your Current Positions")
        frame_positions.place(rely=0.40, relx=0.02, height=300, width=300)

        frame_details = tk.LabelFrame(back_frame, frame_styles,
                                      text="Execution Details")
        frame_details.place(rely=0.03, relx=0.5, height=486, width=440)

        self.label_details = tk.Label(frame_details, justify="left",
                                      bg="#D5D5D5", relief="ridge",
                                      bd=2, font=("Verdana", 10))
        self.label_details.pack(expand=True, fill="both")

        self.entry_units = ttk.Entry(frame_order, width=20, cursor="xterm")
        self.entry_units.place(relx=0.5, rely=0.1)

        self.entry_instruments = ttk.Entry(frame_order, width=20,
                                           cursor="xterm")
        self.entry_instruments.place(relx=0.5, rely=0.3)

        self.check_val = tk.BooleanVar(parent)
        check_btn = tk.Checkbutton(frame_order, variable=self.check_val,
                                   bg="#94b4d1")
        check_btn.place(relx=0.5, rely=0.5)

        btn_exec = ttk.Button(frame_order, text="Execute Trade",
                              command=lambda: self.create_order())
        btn_exec.place(relx=0.57, rely=0.7)

        btn_position = ttk.Button(back_frame, text="Refresh Positions",
                                  command=lambda: self.refresh_positions())
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
        if rows:
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


class AlgoTradingFrame(BaseFrame):
    def __init__(self, parent, app):
        super().__init__(parent)

        text_styles = {"justify": "left",
                       "bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        self.Presenter = p.AlgoTrading(view=self)

        frame_chart = tk.LabelFrame(self, frame_styles,
                                    text="Graph with strategies")
        frame_chart.place(rely=0.40, relx=0.05, relheight=0.55, relwidth=0.9)
        self.canvas_chart = tk.Canvas(frame_chart)
        self.canvas_chart.pack(expand=True, fill="both")

        frame_order = tk.LabelFrame(self, frame_styles,
                                    text="Algorithm Settings")
        frame_order.place(rely=0.05, relx=0.05, height=200, width=400)

        frame_fil = tk.LabelFrame(self, frame_styles,
                                  text="Live Algorithm Responses")
        frame_fil.place(rely=0.05, relx=0.50, height=200, width=400)
        self.label_fil = tk.Label(frame_fil, bg="#D5D5D5",
                                  relief="ridge", bd=3, font=("Verdana", 8))
        self.label_fil.pack(expand=True, fill="both")

        list_strategy = ("Golden Cross", "RSI")
        list_duration = ("1 min", "6 mins", "10 mins", "16 mins", "20 mins")

        self.strategy = tk.StringVar(frame_order)
        self.duration = tk.StringVar(frame_order)

        label_units = tk.Label(frame_order, text_styles, text="Units")
        label_units.place(relx=0.13, rely=0.1)
        label_ccy1 = tk.Label(frame_order, text_styles, text="Currency 1")
        label_ccy1.place(relx=0.13, rely=0.25)
        label_ccy2 = tk.Label(frame_order, text_styles, text="Currency 2")
        label_ccy2.place(relx=0.13, rely=0.40)
        label_strategy = tk.Label(frame_order, text_styles, text="Strategy")
        label_strategy.place(relx=0.13, rely=0.60)
        label_duration = tk.Label(frame_order, text_styles, text="Duration")
        label_duration.place(relx=0.13, rely=0.80)

        self.entry_units = ttk.Entry(frame_order, width=20, cursor="xterm")
        self.entry_units.place(relx=0.35, rely=0.1)
        self.entry_ccy1 = ttk.Entry(frame_order, width=20, cursor="xterm")
        self.entry_ccy1.place(relx=0.35, rely=0.25)
        self.entry_ccy2 = ttk.Entry(frame_order, width=20, cursor="xterm")
        self.entry_ccy2.place(relx=0.35, rely=0.40)

        option_menu_strategy = ttk.OptionMenu(frame_order, self.strategy,
                                              list_strategy[0], *list_strategy)
        option_menu_strategy.place(relx=0.35, rely=0.60)
        option_menu_duration = ttk.OptionMenu(frame_order, self.duration,
                                              list_duration[0], *list_duration)
        option_menu_duration.place(relx=0.35, rely=0.80)

        btn_execution = ttk.Button(frame_order, text="Execute Algorithm",
                                   command=lambda: self.initate_algorithm())
        btn_execution.place(relx=0.69, rely=0.71)
        btn_chart = ttk.Button(frame_order, text="Draw Intraday Chart",
                               command=lambda: self.initiate_algo_chart())
        btn_chart.place(relx=0.69, rely=0.86)

        self.canvas1 = None
        self.counter = 0

    def initate_algorithm(self):
        print("To be reviewed")
        # duration_dict = {"1 min": 1, "6 mins": 6,
        #                  "10 mins": 10, "16 mins": 16,
        #                  "20 mins": 20}
        # get_duration = self.duration.get()
        # duration_minutes = duration_dict.get(get_duration)
        #
        # units = self.units.get()
        # ccy1 = self.entry_ccy1.get()
        # ccy2 = self.entry_ccy2.get()
        # strategy = self.strategy.get()
        # self.Presenter.run_algorithm(timer=duration_minutes,
        #                              units=units,
        #                              currency1=ccy1,
        #                              currency2=ccy2,
        #                              strategy=strategy)

    def initiate_algo_chart(self):
        self.remove_existing_chart()
        ccy1 = self.entry_ccy1.get()
        ccy2 = self.entry_ccy2.get()
        strategy = self.strategy.get()
        self.Presenter.create_algo_chart(currency1=ccy1,
                                         currency2=ccy2,
                                         strategy=strategy)

    def remove_existing_chart(self):
        if self.canvas1:
            self.canvas1.destroy()

    def draw_algo_chart(self, data, strategy):
        figure = plt.Figure(figsize=(4, 5), facecolor="#f0f6f7", dpi=80)
        axis = figure.add_subplot(111)
        axis.tick_params(axis="x", labelsize=9)

        if strategy == "Golden Cross":
            data.plot(kind="line", x="Date", y="Close Price", ax=axis)
            data.plot(kind="line", x="Date", y="5-period SMA value", ax=axis)
            data.plot(kind="line", x="Date", y="15-period SMA value", ax=axis)

        else:
            data.plot(kind="line", x="Date", y="Close Price", ax=axis)
            data.plot(kind="line", x="Date", y="5-period RSI value", ax=axis,
                      secondary_y=True)

        canvas = FigureCanvasTkAgg(figure, self.canvas_chart)
        self.canvas1 = canvas.get_tk_widget()
        self.canvas1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class SecurityPricesFrame(BaseFrame):
    def __init__(self, parent, app):
        super().__init__(parent)

        text_styles = {"bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        self.Presenter = p.SecurityPrices(view=self)

        frame_options = tk.LabelFrame(self, frame_styles,
                                      text="Create a Chart")
        frame_options.place(rely=0.05, relx=0.05, relheight=0.40, relwidth=0.30)
        frame_price = tk.LabelFrame(self, frame_styles, text="Latest Prices")
        frame_price.place(rely=0.50, relx=0.05, relheight=0.30, relwidth=0.30)
        frame_chart = tk.LabelFrame(self, frame_styles, text="Graph")
        frame_chart.place(rely=0.05, relx=0.4, relheight=0.86, relwidth=0.55)

        self.canvas_chart = tk.Canvas(frame_chart, bg="#D5D5D5")
        self.canvas_chart.pack(expand=True, fill="both")

        frame_toolbar = tk.LabelFrame(self, frame_styles,
                                      text="Toolbar Options")
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

        option_menu_period = ttk.OptionMenu(frame_options, self.period,
                                            list_period[0], *list_period)
        option_menu_period.place(relx=0.5, rely=0.40)
        label_period = tk.Label(frame_options, text_styles, text="Period")
        label_period.place(relx=0.24, rely=0.40)

        option_menu_indicator = ttk.OptionMenu(frame_options, self.indicator,
                                               list_indicator[0],
                                               *list_indicator)
        option_menu_indicator.place(relx=0.5, rely=0.55)
        label_indicator = tk.Label(frame_options, text_styles,
                                   text="Indicator")
        label_indicator.place(relx=0.24, rely=0.55)

        btn_draw = ttk.Button(frame_options, text="Draw Chart",
                              command=lambda: self.initiate_chart())
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
    def __init__(self, parent, app):
        super().__init__(parent)

        self.Presenter = p.CurrentPositions(view=self)

        frame1 = tk.LabelFrame(self, frame_styles, text="All Positions")
        frame1.place(rely=0.05, relx=0.05, relheight=0.85, relwidth=0.9)

        btn_position = ttk.Button(self, text="Refresh Positions",
                                  command=lambda: self.refresh_positions())
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
        if rows:
            for row in rows:
                self.tv_positions.insert("", "end", values=row)

    def refresh_positions(self):
        self.clear_positions()
        self.load_positions()


class PositionRecFrame(BaseFrame):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.Presenter = p.PositionReconciliation(view=self)

        frame1 = tk.LabelFrame(self, frame_styles,
                               text="Position Reconciliation")
        frame1.place(rely=0.10, relx=0.05, relheight=0.75, relwidth=0.9)

        btn_position = ttk.Button(self, text="Run Reconciliation",
                                  command=lambda: self.initiate_rec())
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


class TradeBookingsFrame(BaseFrame):
    def __init__(self, parent, app):
        super().__init__(parent)

        text_styles = {"justify": "left",
                       "bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        self.Presenter = p.TradeBookings(view=self)

        frame1 = tk.LabelFrame(self, frame_styles, text="Manual Entry")
        frame1.place(rely=0.05, relx=0.05, relheight=0.20, relwidth=0.55)
        frame2 = tk.LabelFrame(self, frame_styles, text="Cancel/Uncancel Trade")
        frame2.place(rely=0.05, relx=0.60, relheight=0.20, relwidth=0.20)
        frame3 = tk.LabelFrame(self, frame_styles, text="All Transactions")
        frame3.place(rely=0.25, relx=0.05, relheight=0.65, relwidth=0.9)

        label_name = tk.Label(frame1, text_styles, text="Security Name")
        label_name.place(rely=0.05, relx=0.05)
        label_quantity = tk.Label(frame1, text_styles, text="Quantity")
        label_quantity.place(rely=0.3, relx=0.05)
        label_price = tk.Label(frame1, text_styles, text="Price")
        label_price.place(rely=0.55, relx=0.05)

        self.entry_name = ttk.Entry(frame1, width=13, cursor="xterm")
        self.entry_name.place(rely=0.05, relx=0.25)
        self.entry_quantity = ttk.Entry(frame1, width=13, cursor="xterm")
        self.entry_quantity.place(rely=0.3, relx=0.25)
        self.entry_price = ttk.Entry(frame1, width=13, cursor="xterm")
        label_id = tk.Label(frame2, text_styles, text="Order ID")
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
                                 command=lambda: self.add_transaction())
        btn_submit1.place(rely=0.75, relx=0.40)
        btn_submit2 = ttk.Button(frame2, text="Amend Status",
                                 command=lambda: self.change_status())
        btn_submit2.place(rely=0.70, relx=0.35)
        btn_refresh = ttk.Button(frame1, text="Refresh",
                                 command=lambda: self.refresh_transactions())
        btn_refresh.place(rely=0.75, relx=0.60)

        self.tv_transactions = ttk.Treeview(frame3)
        self.tv_transactions.place(relheight=1, relwidth=1)
        ts_transactions = tk.Scrollbar(frame3)
        ts_transactions.configure(command=self.tv_transactions.yview)
        self.tv_transactions.configure(yscrollcommand=ts_transactions.set)
        ts_transactions.pack(side="right", fill="y")
        self.headers = ["Order ID", "Name", "Quantity", "Price", "P&L",
                        "Cancelled"]

        self.load_transaction_headers()
        self.load_transactions()

    def load_transaction_headers(self):
        self.tv_transactions['columns'] = self.headers
        self.tv_transactions["show"] = "headings"
        for header in self.headers:
            self.tv_transactions.heading(header, text=header)
            self.tv_transactions.column(header, width=50)

    def load_transactions(self):
        self.Presenter.get_transactions()

    def clear_transactions(self):
        self.tv_transactions.delete(*self.tv_transactions.get_children())

    def display_transactions(self, rows):
        for row in rows:
            self.tv_transactions.insert("", "end", values=row)

    def refresh_transactions(self):
        self.clear_transactions()
        self.load_transactions()

    def add_transaction(self):
        name = self.entry_name.get()
        quantity = self.entry_quantity.get()
        price = self.entry_price.get()
        self.Presenter.store_transaction(name=name,
                                         quantity=quantity,
                                         price=price)

    def change_status(self):
        toggle = int(self.check_val.get())
        id = self.entry_id.get()
        self.Presenter.set_transaction_status(id, toggle)

    def clear_status_entries(self):
        self.entry_id.delete(0, "end")

    def clear_transaction_entries(self):
        self.entry_name.delete(0, "end")
        self.entry_quantity.delete(0, "end")
        self.entry_price.delete(0, "end")


class UsTreasuryConvWindow(tk.Toplevel):

    def __init__(self):
        super().__init__()

        main_frame = tk.Frame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.geometry("300x200")
        self.resizable(0, 0)

        self.title("T-Bill Conversion")

        self.Presenter = p.UsTreasuryConvWindow(view=self)

        frame1 = tk.LabelFrame(main_frame, frame_styles,
                               text="Enter the price you want to convert")
        frame1.pack(expand=True, fill="both")

        label = tk.Label(frame1, text="Enter price here: ",
                         font=("Trebuchet MS", 9), bg="#94b4d1")
        label.place(rely=0.05, relx=0.05)

        self.entry1 = ttk.Entry(frame1, width=7, cursor="xterm")
        self.entry1.place(rely=0.05, relx=0.50)

        self.label2 = tk.Label(frame1)
        self.label2.place(rely=0.4, relx=0.3, height=75, width=150)

        btn_convert = ttk.Button(frame1, text="Convert price",
                                 command=lambda: self.initiate_conversion())
        btn_convert.place(rely=0.20, relx=0.50)

    def initiate_conversion(self):
        price = self.entry1.get()
        self.Presenter.conversion(price=price)

    def display_conversion(self, new_price):
        self.label2["text"] = new_price


class AboutPageWindow(tk.Toplevel):

    def __init__(self):
        super().__init__()

        main_frame = tk.Frame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.geometry("500x500")
        self.resizable(0, 0)

        self.title("About")
        bio = """PRMSystem is a portfolio management project created by\n
        Ramon Williams. PRMSystem utilises the APIs from AlphaVantage, Oanda\n
        and NewsAPI to create interface that allows the user to read news\n
        articles, check FX prices/charts, execute trades and trade based\n
        on two algorithms. This project also allows you to perform\n
        position reconciliations and store Oanda trades into a database\n
        where ALL entries are logged.

        As I am learning more about software development this project has\n
        improved my knowledge on a variety of python libraries, APIs and SQL\n
        it has also been very helpful on increasing my understanding of\n
        Functions and OOP."""
        frame1 = tk.LabelFrame(main_frame, frame_styles,
                               text="Thank you for viewing")
        frame1.pack(expand=True, fill="both")

        label = tk.Label(frame1, text=bio,
                         font=("Trebuchet MS", 9), bg="#94b4d1")
        label.pack(expand=True)
