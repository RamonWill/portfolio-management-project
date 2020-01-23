import tkinter as tk
from tkinter import ttk
import webbrowser
import APIs.OandaAPI as OandaAPI
from APIs.NewsAPI import latest_news
from APIs.AlgoTradingAPI import Algo
from APIs.VantageAlphaAPI import AV_FXData
from APIs.Calculations import Convertprice
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                               NavigationToolbar2Tk)
import matplotlib.pyplot as plt
import sqlite3


"""This App project will create a python GUI interface that will perform
various portfolio reconciliation tasks and other management data handling"""
# PRMS = Portfolio Reconciliation and Management System

global counter
global current_user
counter = 0
current_user = None

frame_styles = {"relief": "groove",
                "bd": 3, "bg": "#94b4d1",
                "fg": "#073bb3", "font": ("Arial", 9, "bold")}


class LoginPage(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#708090", height=431, width=626)
        main_frame.pack(fill="both", expand="true")

        self.geometry("626x431")  # Sets window size to 626w x 431h pixels
        self.resizable(0, 0)  # This prevents any resizing of the screen

        self.background_image = tk.PhotoImage(file=r"login_background.png")
        background_label = tk.Label(main_frame, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        frame_login = tk.Frame(main_frame, bg="#3F6BAA", relief="groove", bd=2)
        frame_login.place(rely=0.30, relx=0.17, height=130, width=400)

        label_title = ttk.Label(frame_login, text="PRMSystem Login Page", font=("Trebuchet MS Bold", 16), background="#3F6BAA", foreground="#E1FFFF", justify="left")
        label_title.grid(row=0, column=1, columnspan=1)

        label_username = ttk.Label(frame_login, text="Username:", font=("Lucida Sans", 14, "bold"), background="#3F6BAA", foreground="#E1FFFF")
        label_username.grid(row=1, column=0)

        label_password = ttk.Label(frame_login, text="Password:", font=("Lucida Sans", 14, "bold"), background="#3F6BAA", foreground="#E1FFFF")
        label_password.grid(row=2, column=0)

        entry_username = ttk.Entry(frame_login, width=45, cursor="xterm")
        entry_username.grid(row=1, column=1)

        entry_password = ttk.Entry(frame_login, width=45, cursor="xterm", show="*")
        entry_password.grid(row=2, column=1)

        button = ttk.Button(frame_login, text="Login", style="btns.TButton", command=lambda: getlogin())
        button.place(rely=0.70, relx=0.50)

        signup_button = ttk.Button(frame_login, style="btns.TButton", text="Register", command=lambda: get_signup())
        signup_button.place(rely=0.70, relx=0.75)

        s = ttk.Style()
        s.configure("btns.TButton", font=("Arial", 10, "bold"), background="#74CAE3")

        def get_signup():
            SignupPage()

        def getlogin():
            conn = sqlite3.connect("source.db")
            c = conn.cursor()
            global current_user
            user = entry_username.get()
            password = entry_password.get()
            c.execute("""SELECT Username, Password
                         FROM LoginInfo
                         WHERE Username=? AND Password=?""", (user, password,))
            login_check = c.fetchone()

            if login_check:
                tk.messagebox.showinfo("Login Successful",
                                       "Welcome {}".format(user))
                current_user = user
                root.deiconify()
                top.destroy()
            else:
                tk.messagebox.showerror("Information", "The Username or Password you have entered are incorrect ")


class SignupPage(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#3F6BAA", height=150, width=250)
        # pack_propagate prevents the window resizing to match the widgets
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")

        self.geometry("250x150")
        self.resizable(0, 0)

        self.title("Registration")

        label_username = ttk.Label(main_frame, text="New Username:", font=("Lucida Sans", 10, "bold"), background="#3F6BAA", foreground="#E1FFFF")
        label_username.grid(row=1, column=0)

        label_password = ttk.Label(main_frame, text="New Password:", font=("Lucida Sans", 10, "bold"), background="#3F6BAA", foreground="#E1FFFF")
        label_password.grid(row=2, column=0)

        entry_username = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_username.grid(row=1, column=1)

        entry_password = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        entry_password.grid(row=2, column=1)

        label_code = ttk.Label(main_frame, text="Passcode:", font=("Lucida Sans", 10, "bold"), background="#3F6BAA", foreground="#E1FFFF")
        label_code.grid(row=3, column=0)

        entry_code = ttk.Entry(main_frame, width=6, cursor="xterm", show="*")
        entry_code.grid(row=3, column=1)

        button = ttk.Button(main_frame, text="Create Account", command=lambda: signup())
        button.grid(row=4, column=1)

        def signup():
            user = entry_username.get()
            password = entry_password.get()
            passcode = entry_code.get()
            if passcode == "2019" and len(password) > 4:
                conn = sqlite3.connect("source.db")
                c = conn.cursor()
                c.execute("""CREATE TABLE IF NOT EXISTS LoginInfo
                             (Username TEXT, Password TEXT)""")

                c.execute("""SELECT Username
                             FROM LoginInfo
                             WHERE Username=?""", (user,))
                username_check = c.fetchone()
                if username_check is None:
                    c.execute("INSERT INTO LoginInfo VALUES (:Username, :Password)", {"Username": user, "Password": password})
                    conn.commit()
                    c.close()
                    conn.close()
                    tk.messagebox.showinfo("Information", "Your account has now been created.")
                    SignupPage.destroy(self)
                else:
                    tk.messagebox.showerror("Information", "The Username you have entered already exists.")
                    c.close()
                    conn.close()
            else:
                tk.messagebox.showerror("Information", "The Passcode you have entered is incorrect or\nyour password needs to be longer than 4 values.")


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        menu_styles = {"tearoff": 0, "bd": 5,
                       "activebackground": "#d9d9d9",
                       "background": "#FFFFFF",
                       "activeforeground": "#000000"}

        menu_file = tk.Menu(self, menu_styles)
        self.add_cascade(label="File", menu=menu_file)
        menu_file.add_command(label="Homepage", command=lambda: parent.show_frame(HomePage))
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=lambda: parent.Quit_application())

        menu_orders = tk.Menu(self, menu_styles)
        self.add_cascade(label="Market Orders", menu=menu_orders)
        menu_orders.add_command(label="Create Buy/Sell Order", command=lambda: parent.show_frame(CreateOrders))
        menu_orders.add_separator()
        menu_orders.add_command(label="FX Algo Trading", command=lambda: parent.show_frame(AlgoTrading))

        menu_pricing = tk.Menu(self, menu_styles)
        self.add_cascade(label="FX Pricing", menu=menu_pricing)
        menu_pricing.add_command(label="FX Prices/Charts", command=lambda: parent.show_frame(SecurityPrices))

        menu_operations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Operations", menu=menu_operations)
        menu_operations.add_command(label="View Positions", command=lambda: parent.show_frame(CurrentPositions))

        menu_calculations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Tools/Calculators", menu=menu_calculations)
        menu_calculations.add_command(label="32nds/Decimal Converter", command=lambda: parent.Get_treasurypage())
        menu_calculations.add_command(label="Refresh database instruments...", command=lambda: parent.update_instrument_db())

        menu_help = tk.Menu(self, menu_styles)
        self.add_cascade(label="Help", menu=menu_help)
        menu_help.add_command(label="About...")


class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#84CEEB", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.resizable(0, 0)
        self.geometry("1024x600")
        self.frames = {}
        for F in (HomePage, CreateOrders, SecurityPrices, AlgoTrading, CurrentPositions):
            frame = F(main_frame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(HomePage)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def Get_treasurypage(self):
        UsTreasuryConv()

    def update_instrument_db(self):
        OandaAPI.load_instruments()

    def Quit_application(self):
        self.destroy()


class GUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        main_frame = tk.Frame(self, bg="#94b4d1", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)


class HomePage(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        frame_account = tk.LabelFrame(self, frame_styles, text="Account Details")
        frame_account.place(rely=0.05, relx=0.02, height=120, width=300)

        frame_prices = tk.LabelFrame(self, frame_styles, text="Tradable Securities")
        frame_prices.place(rely=0.30, relx=0.02, height=375, width=400)

        frame_news = tk.LabelFrame(self, frame_styles, text="Latest News Headlines")
        frame_news.place(rely=0.05, relx=0.45, height=280, width=550)

        refresh_button = ttk.Button(self, text="Refresh data", command=lambda: Refresh_data())
        refresh_button.place(rely=0.9, relx=0.9)

        frame_chart = tk.LabelFrame(self, frame_styles, text="Positions at a Glance")
        frame_chart.place(rely=0.55, relx=0.45, height=222, width=222)
        pie_chart = tk.Canvas(frame_chart, bg="#D5D5D5", relief="solid", bd=1)
        pie_chart.pack()

        tv1_account = ttk.Treeview(frame_account)
        column_list_account = ["", "Information"]
        tv1_account['columns'] = column_list_account
        tv1_account["show"] = "headings"  # removes empty column
        for column in column_list_account:
            tv1_account.heading(column, text=column)
            tv1_account.column(column, width=75)
        tv1_account.place(relheight=1, relwidth=0.995)

        tv2_prices = ttk.Treeview(frame_prices)
        column_list_prices = ["Instrument", "Bid Price", "Ask Price"]
        tv2_prices['columns'] = column_list_prices
        tv2_prices["show"] = "headings"
        for column in column_list_prices:
            tv2_prices.heading(column, text=column)
            tv2_prices.column(column, width=50)
        tv2_prices.place(relheight=1, relwidth=0.995)
        treescroll_prices = tk.Scrollbar(frame_prices)
        treescroll_prices.configure(command=tv2_prices.yview)
        tv2_prices.configure(yscrollcommand=treescroll_prices.set)
        treescroll_prices.pack(side="right", fill="y")

        tv3_news = ttk.Treeview(frame_news)
        column_list_news = ["Top Headlines", "Source", "Link"]
        tv3_news['columns'] = column_list_news
        tv3_news["show"] = "headings"
        for column in column_list_news:
            if column == "Top Headlines" or column == "Link":
                tv3_news.heading(column, text=column)
                tv3_news.column(column, width=200)
            else:
                tv3_news.heading(column, text=column)
                tv3_news.column(column, width=40)
        tv3_news.place(relheight=1, relwidth=0.995)

        def Open_news_link(event):
            row_id = tv3_news.selection()
            link = tv3_news.item(row_id, "values")[2]
            webbrowser.open_new_tab(link)

        tv3_news.bind("<Double-1>", Open_news_link)  # initiates on 2nd click

        def Load_data():
            account = OandaAPI.Oanda_acc_summary()
            account_rows = account.to_numpy().tolist()
            for row in account_rows:
                tv1_account.insert("", "end", values=row)

            prices = OandaAPI.Oanda_prices()
            price_rows = prices.to_numpy().tolist()
            for row in price_rows:
                tv2_prices.insert("", "end", values=row)

            news = latest_news()
            news_rows = news.to_numpy().tolist()
            for row in news_rows:
                tv3_news.insert("", "end", values=row)

        def Refresh_data():
            tv1_account.delete(*tv1_account.get_children())  # *=splat operator
            tv2_prices.delete(*tv2_prices.get_children())
            tv3_news.delete(*tv3_news.get_children())
            Load_data()

        Load_data()


class CreateOrders(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        back_frame = tk.Frame(self, bg="#94b4d1", relief="groove", bd=3)
        back_frame.place(rely=0.05, relx=0.05, relheight=0.85, relwidth=0.9)

        frame_order = tk.LabelFrame(back_frame, frame_styles, text="Create an Order")
        frame_order.place(rely=0.03, relx=0.02, height=150, width=300)

        label_order_1 = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Units")
        label_order_1.place(relx=0.20, rely=0.1)

        label_order_2 = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Instrument")
        label_order_2.place(relx=0.20, rely=0.3)

        label_order_3 = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Acknowledge")
        label_order_3.place(relx=0.20, rely=0.5)

        frame_positions = tk.LabelFrame(back_frame, frame_styles, text="Your Current Positions")
        frame_positions.place(rely=0.40, relx=0.02, height=300, width=300)

        frame_exec_details = tk.LabelFrame(back_frame, frame_styles, text="Execution Details")
        frame_exec_details.place(rely=0.03, relx=0.5, height=486, width=440)

        label_exec_details = tk.Label(frame_exec_details, justify="left", bg="#D5D5D5", relief="ridge", bd=2, font=("Lucida Sans", 10))
        label_exec_details.pack(expand=True, fill="both")

        entry_units = ttk.Entry(frame_order, width=20, cursor="xterm")
        entry_units.place(relx=0.5, rely=0.1)

        entry_instruments = ttk.Entry(frame_order, width=20,  cursor="xterm")
        entry_instruments.place(relx=0.5, rely=0.3)

        self.check_val = tk.BooleanVar(parent)
        check_btn = tk.Checkbutton(frame_order, variable=self.check_val, bg="#94b4d1")
        check_btn.place(relx=0.5, rely=0.5)

        button = ttk.Button(frame_order, text="Execute Trade", command=lambda: Generateorder())
        button.place(relx=0.57, rely=0.7)

        btn_position = ttk.Button(back_frame, text="Refresh Positions", command=lambda: Refresh_basic_position())
        btn_position.place(relx=0.02, rely=0.35)

        tv1 = ttk.Treeview(frame_positions)
        column_list = ["Instrument", "Units"]
        tv1['columns'] = column_list
        tv1["show"] = "headings"
        for column in column_list:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.place(relheight=1, relwidth=0.995)

        def Load_basic_position():
            try:
                positions = OandaAPI.Open_positions("basic")
                position_rows = positions.to_numpy().tolist()
                for row in position_rows:
                    tv1.insert("", "end", values=row)
            except AttributeError:
                pass

        def Generateorder():
            units = entry_units.get()
            instruments = entry_instruments.get()
            acknowledged = self.check_val.get()
            if acknowledged:
                order_details = OandaAPI.Market_order(units, instruments)
                entry_units.delete(0, "end")
                entry_instruments.delete(0, "end")
                self.check_val.set(False)
                label_exec_details["text"] = OandaAPI.Execution_details(order_details)

            else:
                label_exec_details["text"] = "The trade is not acknowledged.\nYour order has not been sent."

        def Refresh_basic_position():
            tv1.delete(*tv1.get_children())
            Load_basic_position()

        Load_basic_position()


class SecurityPrices(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        frame_options = tk.LabelFrame(self, frame_styles, text="Create a Chart")
        frame_options.place(rely=0.05, relx=0.05, relheight=0.40, relwidth=0.30)
        frame_price = tk.LabelFrame(self, frame_styles, text="Latest Prices")
        frame_price.place(rely=0.50, relx=0.05, relheight=0.30, relwidth=0.30)

        tv1 = ttk.Treeview(frame_price)
        column_list = ["Date", "Price"]
        tv1['columns'] = column_list
        tv1["show"] = "headings"

        for column in column_list:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.place(relheight=1, relwidth=1)

        frame_chart = tk.LabelFrame(self, frame_styles, text="Graph")
        frame_chart.place(rely=0.05, relx=0.4, relheight=0.86, relwidth=0.55)
        canvas_chart = tk.Canvas(frame_chart, bg="#D5D5D5")
        canvas_chart.pack(expand=True, fill="both")

        frame_toolbar = tk.LabelFrame(self, frame_styles, text="Toolbar Options")
        frame_toolbar.place(rely=0.82, relx=0.05, relheight=0.09, relwidth=0.30)
        chart_toolbar = tk.Canvas(frame_toolbar, bg="#D5D5D5")
        chart_toolbar.pack(expand=True, fill="both")

        ccy_1 = ttk.Entry(frame_options, width=6, cursor="xterm")
        ccy_1.place(relx=0.50, rely=0.10)

        label_ccy1 = tk.Label(frame_options, bg="#94b4d1", text="Currency 1", font=("Lucida Sans", 9))
        label_ccy1.place(relx=0.26, rely=0.10)

        ccy_2 = ttk.Entry(frame_options, width=6, cursor="xterm")
        ccy_2.place(relx=0.50, rely=0.25)

        label_ccy2 = tk.Label(frame_options, bg="#94b4d1", text="Currency 2", font=("Lucida Sans", 9))
        label_ccy2.place(relx=0.26, rely=0.25)

        list_period = ("INTRADAY", "DAILY", "WEEKLY")
        list_indicator = ("No Indicator", "SMA", "EMA", "RSI")

        period = tk.StringVar(frame_options)
        indicator = tk.StringVar(frame_options)

        option_menu_period = ttk.OptionMenu(frame_options, period, list_period[0], *list_period)
        option_menu_period.place(relx=0.5, rely=0.40)

        label_period = tk.Label(frame_options, bg="#94b4d1", text="Period", font=("Lucida Sans", 9))
        label_period.place(relx=0.26, rely=0.40)

        option_menu_indicator = ttk.OptionMenu(frame_options, indicator, list_indicator[0], *list_indicator)
        option_menu_indicator.place(relx=0.5, rely=0.55)

        label_indicator = tk.Label(frame_options, bg="#94b4d1", text="Indicator", font=("Lucida Sans", 9))
        label_indicator.place(relx=0.26, rely=0.55)

        button = ttk.Button(frame_options, text="Draw Chart", command=lambda: Generate_chart(self))
        button.place(relx=0.64, rely=0.8)

        self.canvas1 = None
        self.toolbar = None

        def Generate_chart(self):
            try:
                if self.canvas1 is not None:
                    self.canvas1.destroy()
                if self.toolbar is not None:
                    self.toolbar.destroy()
            except AttributeError:
                print("The Canvas is empty")

            param_period = period.get()
            param_indicator = indicator.get()
            param_ccy1 = ccy_1.get()
            param_ccy2 = ccy_2.get()

            figure = plt.Figure(figsize=(4, 5), facecolor="#e3e4de", dpi=80)
            axis = figure.add_subplot(111)

            axis.tick_params(axis="x", labelsize=8)
            x = AV_FXData(param_period, param_ccy1, param_ccy2, param_indicator)
            try:
                df = x.Fx_chart_gui()
                df2 = df.tail(4)
                rsi_check = bool(param_indicator == "RSI")
                ti_list = {"RSI", "SMA", "EMA"}

                df.plot(kind="line", x="Date", y="Close Price", ax=axis)

                if param_indicator in ti_list:
                    df.plot(kind="line", x="Date",
                            y="5-period {} value".format(param_indicator),
                            ax=axis, secondary_y=rsi_check)

                else:
                    pass

                canvas = FigureCanvasTkAgg(figure, canvas_chart)
                self.canvas1 = canvas.get_tk_widget()
                self.canvas1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
                self.toolbar = NavigationToolbar2Tk(canvas, chart_toolbar)

                canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                tv1.delete(*tv1.get_children())
                df2 = df2[["Date", "Close Price"]]
                df2_rows = df2.to_numpy().tolist()
                for row in df2_rows:
                    tv1.insert("", "end", values=row)
            except KeyError:
                print("API Call Delay - Please try again in 1 minute.")


class AlgoTrading(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        frame_chart = tk.LabelFrame(self, frame_styles, text="Graph with strategies")
        frame_chart.place(rely=0.40, relx=0.05, relheight=0.55, relwidth=0.9)
        canvas_chart = tk.Canvas(frame_chart)
        canvas_chart.pack(expand=True, fill="both")

        frame_order = tk.LabelFrame(self, frame_styles, text="Algorithm Settings")
        frame_order.place(rely=0.05, relx=0.05, height=200, width=400)

        frame_fil = tk.LabelFrame(self, frame_styles, text="Live Algorithm Responses")
        frame_fil.place(rely=0.05, relx=0.50, height=200, width=400)
        label_fil = tk.Label(frame_fil, bg="#D5D5D5", relief="ridge", bd=3, font=("Lucida Sans", 8))
        label_fil.pack(expand=True, fill="both")

        list_strategy = ("Golden Cross", "RSI")
        list_duration = ("1 min", "6 mins", "10 mins", "16 mins", "20 mins")

        strategy = tk.StringVar(frame_order)
        duration = tk.StringVar(frame_order)

        label_order_units = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Units")
        label_order_units.place(relx=0.13, rely=0.1)

        label_order_ccy1 = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Currency 1")
        label_order_ccy1.place(relx=0.13, rely=0.25)

        label_order_ccy2 = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Currency 2")
        label_order_ccy2.place(relx=0.13, rely=0.40)

        label_order_strategy = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Strategy")
        label_order_strategy.place(relx=0.13, rely=0.60)

        label_order_duration = tk.Label(frame_order, justify="left", bg="#94b4d1", font=("Lucida Sans", 9), text="Duration")
        label_order_duration.place(relx=0.13, rely=0.80)

        entry_units = ttk.Entry(frame_order, width=20, cursor="xterm")
        entry_units.place(relx=0.35, rely=0.1)

        entry_ccy1 = ttk.Entry(frame_order, width=20, cursor="xterm")
        entry_ccy1.place(relx=0.35, rely=0.25)

        entry_ccy2 = ttk.Entry(frame_order, width=20, cursor="xterm")
        entry_ccy2.place(relx=0.35, rely=0.40)

        option_menu_strategy = ttk.OptionMenu(frame_order, strategy, list_strategy[0], *list_strategy)
        option_menu_strategy.place(relx=0.35, rely=0.60)

        option_menu_duration = ttk.OptionMenu(frame_order, duration, list_duration[0], *list_duration)
        option_menu_duration.place(relx=0.35, rely=0.80)

        btn_execution = ttk.Button(frame_order, text="Execute Algorithm", command=lambda: algo_timer())
        btn_execution.place(relx=0.69, rely=0.71)

        btn_chart = ttk.Button(frame_order, text="Draw Intraday Chart", command=lambda: Generate_algo_chart(self))
        btn_chart.place(relx=0.69, rely=0.86)

        def algo_timer():
            duration_dict = {"1 min": 1, "6 mins": 6, "10 mins": 10, "16 mins": 16, "20 mins": 20}  # minutes in seconds
            global counter
            duration_minutes = duration_dict.get(duration.get())

            while duration_minutes > counter:
                print("order initiated, {} interval elapsed".format(counter))
                root.after(120000, Algorithm_orders())  # 120k millsecs = 2 mins
                counter += 2

            if counter == duration_minutes:
                counter = 0
                print("Time period elapsed")

        def Algorithm_orders():
            units = entry_units.get()
            ccy1 = entry_ccy1.get()
            ccy2 = entry_ccy2.get()
            algo_strategy = strategy.get()
            label_fil["text"] = Algo(ccy1, ccy2).algo_execution(units, algo_strategy)

        self.canvas_chart = None

        def Generate_algo_chart(self):

            if self.canvas_chart:
                self.canvas_chart.destroy()

            ccy1 = entry_ccy1.get()
            ccy2 = entry_ccy2.get()
            param_strategy = strategy.get()

            figure = plt.Figure(figsize=(4, 5), facecolor="#e3e4de", dpi=80)
            axis = figure.add_subplot(111)

            axis.tick_params(axis="x", labelsize=9)

            df = Algo(ccy1, ccy2).live_algo_chart(param_strategy)

            if param_strategy == "Golden Cross":
                df.plot(kind="line", x="Date", y="Close Price", ax=axis)
                df.plot(kind="line", x="Date", y="5-period SMA value", ax=axis)
                df.plot(kind="line", x="Date", y="15-period SMA value", ax=axis)

            else:
                df.plot(kind="line", x="Date", y="Close Price", ax=axis)
                df.plot(kind="line", x="Date", y="5-period RSI value", ax=axis, secondary_y=True)

            canvas = FigureCanvasTkAgg(figure, canvas_chart)
            self.canvas_chart = canvas.get_tk_widget()
            self.canvas_chart.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class CurrentPositions(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        frame1 = tk.LabelFrame(self, frame_styles, text="All Positions")
        frame1.place(rely=0.05, relx=0.05, relheight=0.85, relwidth=0.9)

        tv1 = ttk.Treeview(frame1)
        column_list = ["Instrument", "Units",
                       "Average Price", "Unrealised P&L",
                       "P&L"]
        tv1['columns'] = column_list
        tv1["show"] = "headings"

        for column in column_list:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.place(relheight=1, relwidth=1)

        button_position = ttk.Button(self, text="Refresh Positions", command=lambda: Refresh_advanced_position())
        button_position.place(rely=0.9, relx=0.84)

        def Load_advanced_position():
            positions = OandaAPI.Open_positions("advanced")
            positions_rows = positions.to_numpy().tolist()
            for row in positions_rows:
                tv1.insert("", "end", values=row)

        def Refresh_advanced_position():
            tv1.delete(*tv1.get_children())
            Load_advanced_position()

        Load_advanced_position()


class UsTreasuryConv(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.geometry("300x200")
        self.resizable(0, 0)

        self.title("T-Bill Conversion")

        frame1 = tk.LabelFrame(main_frame, frame_styles, text="Enter the price you want to convert")
        frame1.pack(expand=True, fill="both")

        label = tk.Label(frame1, text="Enter price here: ", font=("Trebuchet MS", 9), bg="#94b4d1")
        label.place(rely=0.05, relx=0.05)

        entry1 = ttk.Entry(frame1, width=7, cursor="xterm")
        entry1.place(rely=0.05, relx=0.50)

        btn_convert = ttk.Button(frame1, text="Convert price", command=lambda: input_price())
        btn_convert.place(rely=0.20, relx=0.50)

        label2 = tk.Label(frame1)
        label2.place(rely=0.4, relx=0.3, height=75, width=150)

        def input_price():
            user_input = entry1.get()
            label2["text"] = Convertprice(user_input)


top = LoginPage()
top.title("PRMSystem Beta 0.9")
root = MyApp()
root.withdraw()
root.title("PRMSystem Beta 0.9")

root.mainloop()
