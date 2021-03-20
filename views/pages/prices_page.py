import tkinter as tk
from tkinter import ttk
from ..basepage import BasePage
from custom_objects.datatable import DataTable
from presenters import PricesPresenter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt


class PricesPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)

        self.presenter = PricesPresenter(
            view=self, alpha_vantage=app.alphavantage_connection
        )

        frame_options = tk.LabelFrame(self, self.frame_styles, text="Create a Chart")
        frame_options.place(rely=0.05, relx=0.05, relheight=0.40, relwidth=0.30)
        frame_price = tk.LabelFrame(self, self.frame_styles, text="Latest Prices")
        frame_price.place(rely=0.50, relx=0.05, relheight=0.30, relwidth=0.30)
        frame_chart = tk.LabelFrame(self, self.frame_styles, text="Graph")
        frame_chart.place(rely=0.05, relx=0.4, relheight=0.86, relwidth=0.55)

        self.canvas_chart = tk.Canvas(frame_chart, bg="#D5D5D5")
        self.canvas_chart.pack(expand=True, fill="both")

        frame_toolbar = tk.LabelFrame(self, self.frame_styles, text="Toolbar Options")
        frame_toolbar.place(rely=0.82, relx=0.05, relheight=0.09, relwidth=0.30)
        self.chart_toolbar = tk.Canvas(frame_toolbar, bg="#D5D5D5")
        self.chart_toolbar.pack(expand=True, fill="both")

        self.entry_ccy1 = ttk.Entry(frame_options, width=6, cursor="xterm")
        self.entry_ccy1.place(relx=0.50, rely=0.10)
        label_ccy1 = tk.Label(frame_options, self.text_styles, text="Currency 1")
        label_ccy1.place(relx=0.24, rely=0.10)

        self.entry_ccy2 = ttk.Entry(frame_options, width=6, cursor="xterm")
        self.entry_ccy2.place(relx=0.50, rely=0.25)
        label_ccy2 = tk.Label(frame_options, self.text_styles, text="Currency 2")
        label_ccy2.place(relx=0.24, rely=0.25)

        list_period = ("INTRADAY", "DAILY", "WEEKLY")
        list_indicator = ("No Indicator", "SMA", "EMA", "RSI")

        self.period = tk.StringVar(frame_options)
        self.indicator = tk.StringVar(frame_options)

        option_menu_period = ttk.OptionMenu(
            frame_options, self.period, list_period[0], *list_period
        )
        option_menu_period.place(relx=0.5, rely=0.40)
        label_period = tk.Label(frame_options, self.text_styles, text="Period")
        label_period.place(relx=0.24, rely=0.40)

        option_menu_indicator = ttk.OptionMenu(
            frame_options, self.indicator, list_indicator[0], *list_indicator
        )
        option_menu_indicator.place(relx=0.5, rely=0.55)
        label_indicator = tk.Label(frame_options, self.text_styles, text="Indicator")
        label_indicator.place(relx=0.24, rely=0.55)

        btn_draw = ttk.Button(
            frame_options, text="Draw Chart", command=self.initiate_chart
        )
        btn_draw.place(relx=0.64, rely=0.8)

        self.price_table = DataTable(frame_price)
        self.price_table.place(relheight=1, relwidth=1)

        self.canvas1 = None
        self.toolbar = None

    def display_prices(self, prices):
        self.price_table.set_datatable_from_object(prices)

    def initiate_chart(self):
        self.remove_existing_chart()
        period = self.period.get()
        indicator = self.indicator.get()
        ccy1 = self.entry_ccy1.get()
        ccy2 = self.entry_ccy2.get()
        self.presenter.create_chart(
            period=period, indicator=indicator, currency1=ccy1, currency2=ccy2
        )

    def remove_existing_chart(self):
        if self.canvas1 is not None:
            self.canvas1.destroy()
        if self.toolbar is not None:
            self.toolbar.destroy()

    def draw_chart(self, indicator=None):
        figure = plt.Figure(figsize=(4, 5), facecolor="#f0f6f7", dpi=80)
        axis = figure.add_subplot(111)
        axis.tick_params(axis="x", labelsize=8)

        rsi_check = bool(indicator == "RSI")
        ti_list = {"RSI", "SMA", "EMA"}
        df = self.price_table.stored_dataframe
        if indicator not in ti_list:
            df.plot(kind="line", x="date", y="close_price", ax=axis)
        else:
            df.plot(kind="line", x="date", y="value", ax=axis)

        canvas = FigureCanvasTkAgg(figure, self.canvas_chart)
        self.canvas1 = canvas.get_tk_widget()
        self.canvas1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.toolbar = NavigationToolbar2Tk(canvas, self.chart_toolbar)

        canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
