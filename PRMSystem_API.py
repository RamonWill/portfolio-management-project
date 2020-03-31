import tkinter as tk
from tkinter import ttk
import Core.OandaAPI as OandaAPI
from Core.AlgoTradingAPI import Algo
from Core.Calculations import Convertprice
from Core.DatabaseConnections import PRMS_Database
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from Setup.setup import Setup_database_tables
import os
from Views import views

"""This App project will create a python GUI interface that will perform
various portfolio reconciliation tasks and other management data handling"""
# PRMS = Portfolio Reconciliation and Management System

# SETUP #
if os.path.exists("source.db"):
    pass
else:
    current_dir = os.getcwd()
    db_path = current_dir + r"\source.db"  # creates the database
    print(Setup_database_tables(db_path))
    OandaAPI.load_instruments()  # loads the security prices to the database
# #

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
        title_styles = {"font": ("Trebuchet MS Bold", 16),
                        "background": "#3F6BAA",
                        "foreground": "#E1FFFF",
                        "justify": "left"}

        text_styles = {"font": ("Verdana", 14),
                       "background": "#3F6BAA",
                       "foreground": "#E1FFFF"}

        self.background_image = tk.PhotoImage(file=r"login_background.png")
        background_label = tk.Label(main_frame, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        frame_login = tk.Frame(main_frame, bg="#3F6BAA", relief="groove", bd=2)
        frame_login.place(rely=0.30, relx=0.17, height=130, width=400)

        label_title = tk.Label(frame_login, title_styles, text="PRMSystem Login Page")
        label_title.grid(row=0, column=1, columnspan=1)

        label_user = tk.Label(frame_login, text_styles, text="Username:")
        label_user.grid(row=1, column=0)

        label_pw = tk.Label(frame_login, text_styles, text="Password:")
        label_pw.grid(row=2, column=0)

        entry_user = ttk.Entry(frame_login, width=45, cursor="xterm")
        entry_user.grid(row=1, column=1)

        entry_pw = ttk.Entry(frame_login, width=45, cursor="xterm", show="*")
        entry_pw.grid(row=2, column=1)

        button = ttk.Button(frame_login, text="Login", style="btns.TButton", command=lambda: getlogin())
        button.place(rely=0.70, relx=0.50)

        signup_btn = ttk.Button(frame_login, style="btns.TButton", text="Register", command=lambda: get_signup())
        signup_btn.place(rely=0.70, relx=0.75)

        label_user = tk.Label(main_frame, font=("Arial Black", 8), background="#3F6BAA", text="Created by Ramon Williams")
        label_user.place(rely=0.9, relx=0.7)

        s = ttk.Style()
        s.configure("btns.TButton", font=("Arial", 10, "bold"), background="#74CAE3")

        def get_signup():
            SignupPage()

        def getlogin():
            global current_user
            user = entry_user.get()
            pw = entry_pw.get()
            with PRMS_Database() as db:
                validation = db.Validate_login(user, pw)

            if validation:
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

        text_styles = {"font": ("Verdana", 10),
                       "background": "#3F6BAA",
                       "foreground": "#E1FFFF"}

        label_user = tk.Label(main_frame, text_styles, text="New Username:")
        label_user.grid(row=1, column=0)

        label_pw = tk.Label(main_frame, text_styles, text="New Password:")
        label_pw.grid(row=2, column=0)

        entry_user = ttk.Entry(main_frame, width=20, cursor="xterm")
        entry_user.grid(row=1, column=1)

        entry_pw = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        entry_pw.grid(row=2, column=1)

        label_code = tk.Label(main_frame, text_styles, text="Passcode:")
        label_code.grid(row=3, column=0)

        entry_code = tk.Entry(main_frame, width=6, cursor="xterm", show="*")
        entry_code.grid(row=3, column=1)

        button = ttk.Button(main_frame, text="Create Account", command=lambda: signup())
        button.grid(row=4, column=1)

        def signup():
            user = entry_user.get()
            pw = entry_pw.get()
            passcode = entry_code.get()

            if passcode == "2019" and len(pw) > 4:
                with PRMS_Database() as db:
                    status = db.registration(user, pw)
                if isinstance(status, str):
                    tk.messagebox.showerror("Information", "The Username you have entered already exists.")
                else:
                    tk.messagebox.showinfo("Information", "Your account has now been created.")
                    SignupPage.destroy(self)
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
        menu_file.add_command(label="Homepage", command=lambda: parent.show_frame(views.HomePageFrame))
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=lambda: parent.Quit_application())

        menu_orders = tk.Menu(self, menu_styles)
        self.add_cascade(label="Market Orders", menu=menu_orders)
        menu_orders.add_command(label="Create Buy/Sell Order", command=lambda: parent.show_frame(views.CreateOrdersFrame))
        menu_orders.add_separator()
        menu_orders.add_command(label="FX Algo Trading", command=lambda: parent.show_frame(AlgoTrading))

        menu_pricing = tk.Menu(self, menu_styles)
        self.add_cascade(label="FX Pricing", menu=menu_pricing)
        menu_pricing.add_command(label="FX Prices/Charts", command=lambda: parent.show_frame(views.SecurityPricesFrame))

        menu_operations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Operations", menu=menu_operations)
        menu_operations.add_command(label="Trade Bookings", command=lambda: parent.show_frame(TradeBookings))
        menu_positions = tk.Menu(menu_operations, menu_styles)
        menu_operations.add_cascade(label="Positions", menu=menu_positions)
        menu_positions.add_command(label="View Positions", command=lambda: parent.show_frame(views.CurrentPositionsFrame))
        menu_positions.add_command(label="Position Reconciliation", command=lambda: parent.show_frame(views.PositionRecFrame))

        menu_calculations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Tools/Calculators", menu=menu_calculations)
        menu_calculations.add_command(label="32nds/Decimal Converter", command=lambda: parent.Get_treasurypage())
        menu_calculations.add_command(label="Refresh database instruments...", command=lambda: parent.update_instrument_db())

        menu_help = tk.Menu(self, menu_styles)
        self.add_cascade(label="Help", menu=menu_help)
        menu_help.add_command(label="About...", command=lambda: parent.AboutMe())


class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#84CEEB", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        self.resizable(0, 0)
        self.geometry("1024x600")
        self.frames = {}
        pages = (views.HomePageFrame, views.CreateOrdersFrame,
                 views.SecurityPricesFrame, AlgoTrading,
                 views.CurrentPositionsFrame, views.PositionRecFrame,
                 TradeBookings)
        for F in pages:
            frame = F(main_frame, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(views.HomePageFrame)
        menubar = MenuBar(self)
        tk.Tk.config(self, menu=menubar)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def Get_treasurypage(self):
        UsTreasuryConv()

    def update_instrument_db(self):
        OandaAPI.load_instruments()

    def AboutMe(self):
        AboutPage()

    def Quit_application(self):
        self.destroy()


class GUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        main_frame = tk.Frame(self, bg="#94b4d1", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")


class AlgoTrading(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        text_styles = {"justify": "left",
                       "bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        frame_chart = tk.LabelFrame(self, frame_styles, text="Graph with strategies")
        frame_chart.place(rely=0.40, relx=0.05, relheight=0.55, relwidth=0.9)
        canvas_chart = tk.Canvas(frame_chart)
        canvas_chart.pack(expand=True, fill="both")

        frame_order = tk.LabelFrame(self, frame_styles, text="Algorithm Settings")
        frame_order.place(rely=0.05, relx=0.05, height=200, width=400)

        frame_fil = tk.LabelFrame(self, frame_styles, text="Live Algorithm Responses")
        frame_fil.place(rely=0.05, relx=0.50, height=200, width=400)
        label_fil = tk.Label(frame_fil, bg="#D5D5D5", relief="ridge", bd=3, font=("Verdana", 8))
        label_fil.pack(expand=True, fill="both")

        list_strategy = ("Golden Cross", "RSI")
        list_duration = ("1 min", "6 mins", "10 mins", "16 mins", "20 mins")

        strategy = tk.StringVar(frame_order)
        duration = tk.StringVar(frame_order)

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
            duration_dict = {"1 min": 1, "6 mins": 6,
                             "10 mins": 10, "16 mins": 16,
                             "20 mins": 20}  # minutes in seconds
            global counter
            duration_minutes = duration_dict.get(duration.get())

            while duration_minutes > counter:
                print("order initiated, {} interval elapsed".format(counter))
                root.after(120000, Algorithm_orders())  # 120k millsecs = 2mins
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

            figure = plt.Figure(figsize=(4, 5), facecolor="#f0f6f7", dpi=80)
            axis = figure.add_subplot(111)

            axis.tick_params(axis="x", labelsize=9)

            df = Algo(ccy1, ccy2).live_algo_chart(param_strategy)

            if param_strategy == "Golden Cross":
                df.plot(kind="line", x="Date", y="Close Price", ax=axis)
                df.plot(kind="line", x="Date", y="5-period SMA value", ax=axis)
                df.plot(kind="line", x="Date", y="15-period SMA value", ax=axis)

            else:
                df.plot(kind="line", x="Date", y="Close Price", ax=axis)
                df.plot(kind="line", x="Date", y="5-period RSI value",
                        ax=axis, secondary_y=True)

            canvas = FigureCanvasTkAgg(figure, canvas_chart)
            self.canvas_chart = canvas.get_tk_widget()
            self.canvas_chart.pack(side=tk.TOP, fill=tk.BOTH, expand=True)


class TradeBookings(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        text_styles = {"justify": "left",
                       "bg": "#94b4d1",
                       "font": ("Verdana", 9)}

        frame1 = tk.LabelFrame(self, frame_styles, text="Manual Entry")
        frame1.place(rely=0.05, relx=0.05, relheight=0.20, relwidth=0.55)

        frame2 = tk.LabelFrame(self, frame_styles, text="Cancel/Uncancel Trade")
        frame2.place(rely=0.05, relx=0.60, relheight=0.20, relwidth=0.20)

        label_name = tk.Label(frame1, text_styles, text="Security Name")
        label_name.place(rely=0.05, relx=0.05)
        label_quantity = tk.Label(frame1, text_styles, text="Quantity")
        label_quantity.place(rely=0.3, relx=0.05)
        label_price = tk.Label(frame1, text_styles, text="Price")
        label_price.place(rely=0.55, relx=0.05)

        entry_name = ttk.Entry(frame1, width=13, cursor="xterm")
        entry_name.place(rely=0.05, relx=0.25)
        entry_quantity = ttk.Entry(frame1, width=13, cursor="xterm")
        entry_quantity.place(rely=0.3, relx=0.25)
        entry_price = ttk.Entry(frame1, width=13, cursor="xterm")
        entry_price.place(rely=0.55, relx=0.25)

        btn_submit1 = ttk.Button(frame1, text="Insert", command=lambda: insert_db())
        btn_submit1.place(rely=0.75, relx=0.40)

        btn_refresh = ttk.Button(frame1, text="Refresh", command=lambda: refresh_db_trans())
        btn_refresh.place(rely=0.75, relx=0.60)

        label_id = tk.Label(frame2, text_styles, text="Order ID")
        label_id.place(rely=0.05, relx=0.05)
        entry_id = ttk.Entry(frame2, width=7, cursor="xterm")
        entry_id.place(rely=0.05, relx=0.35)
        self.check_val = tk.IntVar(parent)
        cancel_btn = tk.Radiobutton(frame2, text="Uncancel", variable=self.check_val, value=0, bg="#94b4d1")
        cancel_btn.place(rely=0.3, relx=0.35)
        uncancel_btn = tk.Radiobutton(frame2, text="Cancel", variable=self.check_val, value=1, bg="#94b4d1")
        uncancel_btn.place(rely=0.5, relx=0.35)
        btn_submit2 = ttk.Button(frame2, text="Amend Status", command=lambda: cancel_db())
        btn_submit2.place(rely=0.70, relx=0.35)

        frame3 = tk.LabelFrame(self, frame_styles, text="All Transactions")
        frame3.place(rely=0.25, relx=0.05, relheight=0.65, relwidth=0.9)

        tv1 = ttk.Treeview(frame3)
        column_list = ["Order ID", "Name",
                       "Quantity", "Price",
                       "P&L", "Cancelled"]
        tv1['columns'] = column_list
        tv1["show"] = "headings"
        for column in column_list:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.place(relheight=1, relwidth=1)
        treescroll_prices = tk.Scrollbar(frame3)
        treescroll_prices.configure(command=tv1.yview)
        tv1.configure(yscrollcommand=treescroll_prices.set)
        treescroll_prices.pack(side="right", fill="y")

        def Load_all_transactions():
            with PRMS_Database() as db:
                positions = db.get_all_positions()
            positions_rows = positions.to_numpy().tolist()
            for row in positions_rows:
                tv1.insert("", "end", values=row)

        def refresh_db_trans():
            tv1.delete(*tv1.get_children())
            Load_all_transactions()

        def insert_db():
            name = entry_name.get()
            quantity = entry_quantity.get()
            price = entry_price.get()

            with PRMS_Database() as db:
                check = db.validate_entry(name, quantity, price)
                if isinstance(check, str):  # if validation Failed
                    print(check)
                    return None
                else:
                    print(db.add_to_db(name, quantity, price))

        def cancel_db():
            toggle = int(self.check_val.get())
            id = entry_id.get()
            with PRMS_Database() as db:
                print(db.cancelled_toggle(id, toggle))

        Load_all_transactions()


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


class AboutPage(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

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
        frame1 = tk.LabelFrame(main_frame, frame_styles, text="Thank you for viewing")
        frame1.pack(expand=True, fill="both")

        label = tk.Label(frame1, text=bio, font=("Trebuchet MS", 9), bg="#94b4d1")
        label.pack(expand=True)


top = LoginPage()
top.title("PRMSystem")
root = MyApp()
root.withdraw()
root.title("PRMSystem")

root.mainloop()
