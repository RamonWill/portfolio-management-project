import tkinter as tk
import Core.OandaAPI as OandaAPI
from Setup.setup import Setup_database_tables, check_configurations
import os
from Views import views, navigation, auth
from Core.config import Configurations

# Portfolio Reconciliation and Management System (PRMS)

DATABASE_NAME = Configurations.DATABASE_NAME
# SETUP #
check_configurations()

if not os.path.exists(DATABASE_NAME):
    current_dir = os.getcwd()
    db_path = current_dir + r"\{}".format(DATABASE_NAME)  # create database
    Setup_database_tables(db_path)
    OandaAPI.load_instruments()  # loads the security prices to the database
###


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PRMSystem")
        main_frame = tk.Frame(self, bg="#84CEEB", height=600, width=1024)
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")
        self.resizable(0, 0)
        self.geometry("1024x600")
        self.frames = {}
        pages = (views.HomePageFrame,
                 views.CreateOrdersFrame,
                 views.SecurityPricesFrame,
                 views.AlgoTradingFrame,
                 views.CurrentPositionsFrame,
                 views.PositionRecFrame,
                 views.TradeBookingsFrame)

        for page in pages:
            frame = page(parent=main_frame, app=self)
            self.frames[page] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(views.HomePageFrame)
        menubar = navigation.NavBar(self)
        tk.Tk.config(self, menu=menubar)

        auth.LoginPage(parent=self)

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def show_converter(self):
        views.UsTreasuryConvWindow()

    def update_instrument_db(self):
        OandaAPI.load_instruments()

    def AboutMe(self):
        views.AboutPageWindow()

    def Quit_application(self):
        self.destroy()


if __name__ == "__main__":
    root = Application()
    root.withdraw()
    root.mainloop()
