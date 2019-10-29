import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk
import APIs.OandaAPI as OandaAPI
import APIs.NewsAPI as NewsAPI
import APIs.AlgoTradingAPI as Algo
import APIs.VantageAlphaAPI as AVantageAPI
import APIs.calculations as calculations
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
import sqlite3


"""This App project will create a python GUI interface that will perform
various portfolio reconciliation tasks and other management data handling"""
# PRMS = Portfolio Reconciliation and Management System

global counter
global current_user
counter = 0
current_user = None

screen_height = 600
screen_width = 1024


class LoginPage(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#6D7993", height=431, width=626)
        main_frame.pack(fill="both",expand="true")

        self.geometry("626x431") #This will fix the size of the app to 626width, 431height pixels
        self.resizable(0, 0) #This prevents any resizing of the screen

        self.background_image = tk.PhotoImage(file = r"C:\Users\Owner\Documents\PRMS_API\home_login_background.png")
        background_label = tk.Label(main_frame, image=self.background_image)
        background_label.place(relwidth=1,relheight=1)

        secondary_frame = tk.Frame(main_frame, bg="#6D7993", relief="groove", bd=4)
        secondary_frame.place(rely=0.25, relx=0.15, height=170, width=400)

        label_title = tk.Label(secondary_frame, text="PRMSystem Login Page", font=("Trebuchet MS Bold",16), bg="#6D7993", fg="#483F44", justify="left")
        label_title.grid(row=0, column=1, columnspan=1)

        label_username = tk.Label(secondary_frame, text="Username:", font=("Lucida Sans",14,"bold"), bg="#6D7993", fg="#483F44")
        label_username.grid(row=1, column=0)

        label_password = tk.Label(secondary_frame, text="Password:", font=("Lucida Sans",14,"bold"), bg="#6D7993", fg="#483F44")
        label_password.grid(row=2, column=0)

        entry_username = tk.Entry(secondary_frame, width=45, relief="ridge",bd=2, bg="#fbfbfb")
        entry_username.grid(row=1, column=1)

        entry_password = tk.Entry(secondary_frame, width=45, relief="ridge", bd=2, show="*", bg="#fbfbfb")
        entry_password.grid(row=2, column=1)

        button = tk.Button(secondary_frame, text="  Login  ", relief="groove", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 12, "bold"), command = lambda: getlogin())
        button.grid(row=3,column=1)

        signup_button = tk.Button(secondary_frame, text="Register", relief="groove", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 12, "bold"), command = lambda: get_signup())
        signup_button.grid(row=4,column=1)

        def get_signup():
            SignupPage()

        def getlogin():
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            global current_user
            user = entry_username.get()
            password = entry_password.get()
            c.execute("SELECT Username, Password FROM LoginInfo WHERE Username=? AND Password=?",(user, password,))
            login_check = c.fetchone()

            if login_check:
                tk.messagebox.showinfo("Login Successful","Welcome {}".format(user))
                current_user = user
                root.deiconify()
                top.destroy()
            else:
                tk.messagebox.showinfo("Information", "The Username or Password you have entered are incorrect")

class SignupPage(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)

        main_frame = tk.Frame(self, bg="#6D7993", height=150, width=250)
        main_frame.pack_propagate(0) #Doesn't allow the widgets inside a frame to determine the frame's width / height
        main_frame.pack(fill="both",expand="true")

        self.geometry("250x150") #This will fix the size of the app to 626width, 431height pixels
        self.resizable(0, 0) #This prevents any resizing of the screen

        background_label = tk.Label(main_frame, bg="#6D7993")
        background_label.place(relwidth=1,relheight=1)

        label_username = tk.Label(background_label, text="New Username:", font=("Lucida Sans",10,"bold"), bg="#6D7993", fg="#483F44")
        label_username.grid(row=1, column=0)

        label_password = tk.Label(background_label, text="New Password:", font=("Lucida Sans",10,"bold"), bg="#6D7993", fg="#483F44")
        label_password.grid(row=2, column=0)

        entry_username = tk.Entry(background_label, width=20, relief="ridge",bd=2, bg="#fbfbfb")
        entry_username.grid(row=1, column=1)

        entry_password = tk.Entry(background_label, width=20, relief="ridge", bd=2, show="*", bg="#fbfbfb")
        entry_password.grid(row=2, column=1)

        label_code = tk.Label(background_label, text="Passcode:", font=("Lucida Sans",10,"bold"), bg="#6D7993", fg="#483F44")
        label_code.grid(row=3, column=0)

        entry_code = tk.Entry(background_label, width=6, relief="ridge", bd=2, show="*", bg="#fbfbfb")
        entry_code.grid(row=3, column=1)

        button = tk.Button(background_label, text=" Sign Up ", relief="groove", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 9, "bold"), command = lambda: signup())
        button.grid(row=4,column=1)

        def signup():
            user = entry_username.get()
            password = entry_password.get()
            passcode = entry_code.get()
            if passcode == "2019" and len(password) > 4:
                conn = sqlite3.connect("users.db")
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS LoginInfo (Username TEXT, Password TEXT)")
                c.execute("SELECT Username FROM LoginInfo WHERE Username=?",(user,))
                username_check = c.fetchone()
                if username_check == None:
                    c.execute("INSERT INTO LoginInfo VALUES (:Username, :Password)", {"Username":user, "Password":password})
                    conn.commit()
                    c.close()
                    conn.close()
                    tk.messagebox.showinfo("Information", "Your new account has now been created.")
                    SignupPage.destroy(self)
                else:
                    tk.messagebox.showinfo("Information", "The Username you have entered already exists.")
            else:
                tk.messagebox.showinfo("Information", "The Passcode you have entered is incorrect or\nyour password needs to be longer than 4 values.")


class MenuBar(tk.Menu):
    def __init__(self, parent):
        tk.Menu.__init__(self, parent)

        menu_file = tk.Menu(self, tearoff=0, bg="#BFBFBF", activebackground= "#96858F")
        self.add_cascade(label="File", menu=menu_file)
        menu_file.add_command(label= "Homepage", command= lambda:parent.show_frame(HomePage))
        menu_file.add_separator()
        menu_file.add_command(label= "Exit", command= lambda: parent.Quit_application())

        menu_orders = tk.Menu(self, tearoff=0, bg="#BFBFBF", activebackground= "#96858F")
        self.add_cascade(label= "Market Orders", menu=menu_orders)
        menu_orders.add_command(label= "Create Buy/Sell Order", command = lambda:parent.show_frame(CreateOrders))
        menu_orders.add_separator()
        menu_orders.add_command(label= "FX Algo Trading", command = lambda:parent.show_frame(AlgoTrading))

        menu_pricing = tk.Menu(self, tearoff=0, bg="#BFBFBF", activebackground= "#96858F")
        self.add_cascade(label= "FX Pricing", menu=menu_pricing)
        menu_pricing.add_command(label= "FX Prices/Charts", command = lambda:parent.show_frame(SecurityPrices))

        menu_operations = tk.Menu(self, tearoff=0, bg="#BFBFBF", activebackground= "#96858F")
        self.add_cascade(label= "Operations", menu=menu_operations)
        menu_operations.add_command(label= "View Positions", command= lambda:parent.show_frame(CurrentPositions))

        menu_calculations = tk.Menu(self, tearoff=0, bg="#BFBFBF", activebackground= "#96858F")
        self.add_cascade(label= "Tools/Calculators", menu=menu_calculations)
        menu_calculations.add_command(label= "32nds/Decimal Converter", command=lambda: parent.Get_treasurypage())

        menu_help = tk.Menu(self, tearoff=0, bg="#BFBFBF", activebackground= "#96858F")
        self.add_cascade(label="Help", menu=menu_help)
        menu_help.add_command(label="About...")


class MyApp(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#84CEEB", height=screen_height, width=screen_width)
        main_frame.pack_propagate(0) #Doesn't allow the widgets inside a frame to determine the frame's width / height
        main_frame.pack(fill="both",expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        self.resizable(0, 0) #This prevents any resizing of the screen
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

    def Quit_application(self):
        self.destroy()

class GUI(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        main_frame = tk.Frame(self, bg="#6D7993", height=screen_height, width=screen_width)
        main_frame.pack_propagate(0) #Doesn't allow the widgets inside a frame to determine the frame's width / height
        main_frame.pack(fill="both",expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)


class HomePage(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        frame_account = tk.Frame(self, relief="ridge", bd=3)
        frame_account.place(rely=0.10, relx=0.02, height=150, width=300)

        frame_prices = tk.Frame(self, relief="ridge", bd=3)
        frame_prices.place(rely=0.40, relx=0.02, height=300, width=500)

        frame_news = tk.Frame(self, relief="ridge", bd=3)
        frame_news.place(rely=0.10, relx=0.57, height=480, width=400)

        button_position_rec = tk.Button(self, text="Refresh data", bg= "#aaaaaa", fg ="#483F44", relief="groove",
         font=("Arial", 8, "bold"), command = lambda: Refresh_data())
        button_position_rec.place(rely=0.055, relx=0.02)



        tv1_account = ttk.Treeview(frame_account)
        column_list_account = ["", "Account Details"]
        tv1_account['columns'] = column_list_account
        tv1_account["show"] = "headings" # removes empty column
        for column in column_list_account:
            tv1_account.heading(column, text=column)
            tv1_account.column(column, width=75)
        tv1_account.grid(sticky = ("N","S","W","E"))
        self.treeview = tv1_account
        tv1_account.place(relheight=1,relwidth=1)


        tv2_prices = ttk.Treeview(frame_prices)
        column_list_prices = ["Instrument", "Bid Price", "Ask Price"]
        tv2_prices['columns'] = column_list_prices
        tv2_prices["show"] = "headings" # removes empty column
        for column in column_list_prices:
            tv2_prices.heading(column, text=column)
            tv2_prices.column(column, width=50)
        tv2_prices.grid(sticky = ("N","S","W","E"))
        self.treeview = tv2_prices
        tv2_prices.place(relheight=1,relwidth=1)
        treescroll_prices = ttk.Scrollbar(frame_prices)
        treescroll_prices.configure(command=tv2_prices.yview)
        tv2_prices.configure(yscrollcommand=treescroll_prices.set)
        treescroll_prices.pack(side="right", fill="y")

        tv3_news = ttk.Treeview(frame_news)
        column_list_news = ["Title", "Source", "Link"]
        tv3_news['columns'] = column_list_news
        tv3_news["show"] = "headings" # removes empty column
        for column in column_list_news:
            if column == "Source":
                tv3_news.heading(column, text=column)
                tv3_news.column(column, width=30)
            else:
                tv3_news.heading(column, text=column)
                tv3_news.column(column, width=100)
        tv3_news.grid(sticky = ("N","S","W","E"))
        self.treeview = tv3_news
        tv3_news.place(relheight=1,relwidth=1)
        treescroll_news = ttk.Scrollbar(frame_news, orient="horizontal")
        treescroll_news.configure(command=tv3_news.xview)
        tv3_news.configure(xscrollcommand=treescroll_news.set)
        treescroll_news.pack(side="bottom", fill="x")


        def Load_data():
            account = OandaAPI.Oanda_acc_summary()
            for index in range((account.shape[0])):
                row_data = list(account.iloc[index])
                tv1_account.insert("","end", values=row_data)

            prices = OandaAPI.Oanda_prices()
            for index in range((prices.shape[0])):
                row_data = list(prices.iloc[index])
                tv2_prices.insert("","end", values=row_data)

            news = NewsAPI.latest_news_headlines()
            for index in range((news.shape[0])):
                row_data = list(news.iloc[index])
                tv3_news.insert("","end", values=row_data)

        def Refresh_data():
            tv1_account.delete(*tv1_account.get_children()) #* is a splat operator
            tv2_prices.delete(*tv2_prices.get_children())
            tv3_news.delete(*tv3_news.get_children())
            Load_data()

        Load_data()


class CreateOrders(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        secondary_frame = tk.Frame(self, bg="#9099A2")
        secondary_frame.place(rely=0.05, relx = 0.05, relheight=0.85, relwidth=0.9)

        frame_order = tk.Frame(secondary_frame, bg="#D5D5D5", relief="ridge", bd=3)
        frame_order.place(rely=0.03, relx=0.02, height=150, width=300)

        label_order_1 = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Units")
        label_order_1.place(relx=0.22, rely=0.1)

        label_order_2 = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Instrument")
        label_order_2.place(relx=0.22, rely=0.3)

        label_order_3 = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Password")
        label_order_3.place(relx=0.22, rely=0.5)

        label_position = tk.Label(secondary_frame, text="current positions", justify="left", bg="#D5D5D5", relief="ridge", bd=3)
        label_position.place(rely=0.40, relx=0.02, height=300, width=300)

        tv1 = ttk.Treeview(label_position)
        column_list = ["Instrument", "Units"]
        tv1['columns'] = column_list
        tv1["show"] = "headings" # removes empty column

        for column in column_list:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.grid(sticky = ("N","S","W","E"))
        self.treeview = tv1
        tv1.place(relheight=1, relwidth=1)

        label_exec_details = tk.Label(secondary_frame, justify="left", bg="#D5D5D5", relief="ridge", bd=3, font=("Lucida Sans",10))
        label_exec_details.place(rely=0.03, relx=0.5, height=486, width=440)

        entry_units = tk.Entry(frame_order, width=20, relief="sunken",bd=3)
        entry_units.place(relx=0.5, rely=0.1)

        entry_instruments = tk.Entry(frame_order, width=20, relief="sunken",bd=3)
        entry_instruments.place(relx=0.5, rely=0.3)

        entry_password = tk.Entry(frame_order, width=20, relief="sunken",bd=3, show="*")
        entry_password.place(relx=0.5, rely=0.5)

        button = tk.Button(frame_order, text="Execute Trade", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 10, "bold"), relief="groove",
        command = lambda: Generateorder())
        button.place(relx=0.57, rely=0.7)

        button_position = tk.Button(secondary_frame, text="Refresh Positions", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 8,"bold"), relief="groove",
        command = lambda: Refresh_basic_position())
        button_position.place(relx=0.02, rely=0.35)


        def Load_basic_position():
            account = OandaAPI.Open_positions("basic")
            for index in range((account.shape[0])):
                row_data = list(account.iloc[index])
                tv1.insert("","end", values=row_data)


        def Generateorder():
            units = entry_units.get()
            instruments = entry_instruments.get()
            password = entry_password.get()

            if password == "trade":
                order_details = OandaAPI.Market_order(units, instruments, password)

                entry_units.delete(0,"end")
                entry_instruments.delete(0,"end")
                entry_password.delete(0,"end")
                label_exec_details["text"] = OandaAPI.Execution_details(order_details)

            else:
                label_exec_details["text"] = "Incorrect Password"



        def Refresh_basic_position():
            tv1.delete(*tv1.get_children()) #check what a splat operator is. its the * in this line
            Load_basic_position()

        Load_basic_position()


class SecurityPrices(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        frame_chart_info = tk.Frame(self, bg="#D5D5D5", relief="ridge", bd=3)
        frame_chart_info.place(rely=0.05, relx = 0.05, relheight=0.40, relwidth=0.30)
        frame_price_table = tk.Frame(self, bg="#D5D5D5", relief="ridge", bd=3)
        frame_price_table.place(rely=0.50, relx = 0.05, relheight=0.30, relwidth=0.30)

        tv1 = ttk.Treeview(frame_price_table)
        column_list = ["Date", "Price"]
        tv1['columns'] = column_list
        tv1["show"] = "headings" # removes empty column

        for column in column_list:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.grid(sticky = ("N","S","W","E"))
        self.treeview = tv1
        tv1.place(relheight=1, relwidth=1)


        canvas_chart = tk.Canvas(self, bg="#D5D5D5", relief="ridge", bd=2)
        canvas_chart.place(rely=0.05, relx = 0.4, relheight=0.85, relwidth=0.55)

        canvas_chart_toolbar = tk.Canvas(self, relief="ridge", bd=2)
        canvas_chart_toolbar.place(rely=0.82, relx = 0.05, relheight=0.08, relwidth=0.30)

        ccy_1 = tk.Entry(frame_chart_info, width=6, relief="sunken",bd=4)
        ccy_1.place(relx=0.50, rely=0.10)

        label_ccy1 = tk.Label(frame_chart_info, bg="#D5D5D5", text="Currency 1", font=("Lucida Sans",9))
        label_ccy1.place(relx=0.26, rely = 0.10)

        ccy_2 = tk.Entry(frame_chart_info, width=6, relief="sunken",bd=3)
        ccy_2.place(relx=0.50, rely=0.25)

        label_ccy2 = tk.Label(frame_chart_info, bg="#D5D5D5", text="Currency 2", font=("Lucida Sans",9))
        label_ccy2.place(relx=0.26, rely = 0.25)

        list_period = ("INTRADAY", "DAILY", "WEEKLY")
        list_indicator = ("No Indicator", "SMA", "EMA", "RSI")

        period = tk.StringVar(frame_chart_info)
        period.set(list_period[0]) # default value

        indicator = tk.StringVar(frame_chart_info)
        indicator.set(list_indicator[0]) # default value

        option_menu_period = tk.OptionMenu(frame_chart_info, period, *list_period)
        option_menu_period.place(relx=0.5, rely=0.40)

        label_period = tk.Label(frame_chart_info, bg="#D5D5D5", text="Period", font=("Lucida Sans",9))
        label_period.place(relx=0.26, rely = 0.40)

        option_menu_indicator = tk.OptionMenu(frame_chart_info, indicator, *list_indicator)
        option_menu_indicator.place(relx=0.5, rely=0.55)

        label_indicator = tk.Label(frame_chart_info, bg="#D5D5D5", text="Indicator", font=("Lucida Sans",9))
        label_indicator.place(relx=0.26, rely = 0.55)


        button = tk.Button(frame_chart_info, text="Draw Chart", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 8,"bold"), relief="groove", command = lambda: Generate_chart(self))
        button.place(relx=0.64, rely=0.8)


        self.canvas1 = None
        self.toolbar = None

        def Generate_chart(self):

            if self.canvas1 != None:
                self.canvas1.destroy()
            if self.toolbar != None:
                self.toolbar.destroy()

            param_period = period.get()
            param_indicator = indicator.get()
            param_ccy1 = ccy_1.get()
            param_ccy2 = ccy_2.get()

            figure= plt.Figure(figsize=(4,5),facecolor="#96858F", dpi=100)
            axis=figure.add_subplot(111)

            df = AVantageAPI.Fx_chart_gui(param_period, param_ccy1, param_ccy2, param_indicator)
            df2 = df.tail(4)
            rsi_check = bool(param_indicator == "RSI")
            ti_list = {"RSI", "SMA", "EMA"}

            df.plot(kind="line", x="Date", y="Close Price", ax=axis)

            if param_indicator in ti_list:
                df.plot(kind="line", x="Date", y="{} value".format(param_indicator),
                ax=axis, secondary_y=rsi_check)

            else:
                pass

            canvas=FigureCanvasTkAgg(figure, canvas_chart)
            self.canvas1 = canvas.get_tk_widget()
            self.canvas1.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            self.toolbar = NavigationToolbar2Tk(canvas, canvas_chart_toolbar)


            canvas._tkcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tv1.delete(*tv1.get_children())
            df2 = df2[["Date","Close Price"]]
            for index in range((df2.shape[0])):
                row_data = list(df2.iloc[index])
                tv1.insert("","end", values=row_data)


class AlgoTrading(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        canvas_chart = tk.Canvas(self)
        canvas_chart.place(rely=0.40, relx = 0.05, relheight=0.55, relwidth=0.9)

        frame_order = tk.Frame(self, bg="#D5D5D5", relief="ridge", bd=3)
        frame_order.place(rely=0.05, relx=0.05, height=200, width=400)

        label_fil = tk.Label(self, bg="#D5D5D5", relief="ridge", bd=3, font=("Lucida Sans",8))
        label_fil.place(rely=0.05, relx=0.50, height=200, width=400)

        list_strategy = ("Golden Cross", "RSI")
        list_duration = ("1 min", "6 mins", "10 mins", "16 mins", "20 mins")

        strategy = tk.StringVar(frame_order)
        strategy.set(list_strategy[0]) # default value

        duration = tk.StringVar(frame_order)
        duration.set(list_duration[0]) # default value

        label_order_units = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Units")
        label_order_units.place(relx=0.13, rely=0.1)

        label_order_ccy1 = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Currency 1")
        label_order_ccy1.place(relx=0.13, rely=0.25)

        label_order_ccy2 = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Currency 2")
        label_order_ccy2.place(relx=0.13, rely=0.40)

        label_order_strategy = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Strategy")
        label_order_strategy.place(relx=0.13, rely=0.60)

        label_order_duration = tk.Label(frame_order, justify="left", bg="#D5D5D5", font=("Lucida Sans",9), text="Duration")
        label_order_duration.place(relx=0.13, rely=0.80)


        entry_units = tk.Entry(frame_order, width=20, relief="sunken",bd=3)
        entry_units.place(relx=0.35, rely=0.1)

        entry_ccy1 = tk.Entry(frame_order, width=20, relief="sunken",bd=3)
        entry_ccy1.place(relx=0.35, rely=0.25)

        entry_ccy2 = tk.Entry(frame_order, width=20, relief="sunken",bd=3)
        entry_ccy2.place(relx=0.35, rely=0.40)

        option_menu_strategy = tk.OptionMenu(frame_order, strategy, *list_strategy)
        option_menu_strategy.place(relx=0.35, rely=0.60)

        option_menu_duration = tk.OptionMenu(frame_order, duration, *list_duration)
        option_menu_duration.place(relx=0.35, rely=0.80)

        button_execution = tk.Button(frame_order, text="Execute Algorithm", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 8,"bold"), relief="groove", command = lambda: algo_timer())
        button_execution.place(relx=0.69, rely=0.72)

        button_chart = tk.Button(frame_order, text="Draw Intraday Chart", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 8,"bold"), relief="groove", command = lambda: Generate_algo_chart(self))
        button_chart.place(relx=0.69, rely=0.86)


        def algo_timer():
            duration_dict = {"1 min":1, "6 mins":6, "10 mins":10, "16 mins":16, "20 mins":20} # minutes in seconds
            global counter
            duration_minutes = duration_dict.get(duration.get())
            units = entry_units.get()
            ccy1 = entry_ccy1.get()
            ccy2 = entry_ccy2.get()
            algo_strategy = strategy.get()


            while duration_minutes > counter:
                print("order initiated, {} interval elapsed".format(counter))
                root.after(120000, Algorithm_orders()) #120k millsecs = 2 mins
                counter += 2

            if counter == duration_minutes:
                counter = 0
                print("Time period elapsed")

        def Algorithm_orders():
            units = entry_units.get()
            ccy1 = entry_ccy1.get()
            ccy2 = entry_ccy2.get()
            algo_strategy = strategy.get()
            label_fil["text"] = Algo.algo_execution(units, ccy1, ccy2, algo_strategy)

        self.canvas_chart = None


        def Generate_algo_chart(self):

            if self.canvas_chart:
                self.canvas_chart.destroy()

            ccy1 = entry_ccy1.get()
            ccy2 = entry_ccy2.get()
            param_strategy = strategy.get()


            figure= plt.Figure(figsize=(4,5),facecolor="#96858F", dpi=100)
            axis=figure.add_subplot(111)
            figure.autofmt_xdate()
            df = Algo.live_algo_chart(ccy1, ccy2, param_strategy)

            if param_strategy == "Golden Cross":
                df.plot(kind="line", x="Date", y="Close Price", ax=axis)
                df.plot(kind="line", x="Date", y="5-day SMA value", ax=axis)
                df.plot(kind="line", x="Date", y="15-day SMA value", ax=axis)

            else:
                df.plot(kind="line", x="Date", y="Close Price", ax=axis)
                df.plot(kind="line", x="Date", y="5-day RSI value", ax=axis, secondary_y=True)

            canvas=FigureCanvasTkAgg(figure, canvas_chart)
            self.canvas_chart = canvas.get_tk_widget()
            self.canvas_chart.pack(side=tk.TOP, fill=tk.BOTH, expand=True)



class CurrentPositions(GUI):
    def __init__(self, parent, controller):
        GUI.__init__(self, parent)

        secondary_frame = tk.Frame(self)
        secondary_frame.place(rely=0.05, relx = 0.05, relheight=0.85, relwidth=0.9)


        tv1 = ttk.Treeview(secondary_frame)
        column_list = ["Instrument", "Units", "Average Price", "Unrealised P&L", "P&L"]
        tv1['columns'] = column_list
        tv1["show"] = "headings"

        for column in column_list:
            tv1.heading(column, text=column)
            tv1.column(column, width=50)
        tv1.grid(sticky = ("N","S","W","E"))
        self.treeview = tv1
        tv1.place(relheight=1, relwidth=1)

        button_position = tk.Button(self, text="Refresh Positions", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 8,"bold"), relief="groove",
         command = lambda: Refresh_advanced_position())
        button_position.place(rely=0.9, relx = 0.84)

        def Load_advanced_position():
            account = OandaAPI.Open_positions("advanced")
            for index in range((account.shape[0])):
                row_data = list(account.iloc[index])
                tv1.insert("","end", values=row_data)

        def Refresh_advanced_position():
            tv1.delete(*tv1.get_children())
            Load_advanced_position()

        Load_advanced_position()


class UsTreasuryConv(tk.Tk):

    def __init__(self, *args, **kwargs):

        tk.Tk.__init__(self, *args, **kwargs)
        main_frame = tk.Frame(self, bg="#6D7993", height=325, width=400, bd=5)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both",expand="true")
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        self.geometry("400x325")
        self.resizable(0, 0)

        label = tk.Label(main_frame, text="32nds/Decimal Converter", font=("Trebuchet MS",16), bg = "#6D7993" )
        label.pack(pady=10, padx=10)

        label1 = tk.Label(main_frame, text="Enter a US Treasury Price in either 32nds or Decimal:", justify="left"
        , font=("Lucida Sans",8), bg = "#6D7993")
        label1.place(rely=0.25, relx=0.02, height=30, width=300)

        entry1 = tk.Entry(main_frame, width=7, relief="sunken",bd=3)
        entry1.place(rely=0.25, relx=0.80, width=50, height=30)

        button_convert = tk.Button(main_frame, text="Convert price", bg= "#aaaaaa", fg ="#483F44", font=("Arial", 9,"bold"), command= lambda: input_price())
        button_convert.place(rely = 0.40, relx=0.40)

        def input_price():
            user_input = entry1.get()
            label2["text"] = calculations.Convertprice(user_input)

        label2 = tk.Label(main_frame)
        label2.place(rely=0.6, relx=0.27, height=75, width=175)


top = LoginPage()
top.title("PRMSystem Beta 0.9")
root = MyApp()
root.withdraw()
root.title("PRMSystem Beta 0.9")



root.mainloop()
