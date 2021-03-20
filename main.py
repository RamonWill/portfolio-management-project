import tkinter as tk
from tkinter import messagebox
from navigation import Navbar
from views import HomePage, AboutWindow, CalculationsWindow, LoginWindow
from external_connections import NewsConnection, AlphaVantageAPI, OandaConnection
from models import PRMS_Database
from authentication import Authenticator

# Portfolio Reconciliation and Management System (PRMS)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PRMSystem")
        self.main_frame = tk.Frame(self, bg="#84CEEB")
        self.main_frame.pack(fill="both", expand="true")
        self.main_frame.pack_propagate(0)
        self.geometry("1024x600")
        self.resizable(0, 0)
        self.db = PRMS_Database()
        self.alphavantage_connection = AlphaVantageAPI(api_key="")
        self.news_connection = NewsConnection("")
        self.oanda_connection = OandaConnection(account_id="", api_key="")

        self.current_page = tk.Frame()
        self.show_frame(HomePage)
        menubar = Navbar(root=self)
        tk.Tk.config(self, menu=menubar)

        self.authenticator = Authenticator(self.db)
        LoginWindow(parent=self, authenticator=self.authenticator)
        self.protocol("WM_DELETE_WINDOW", self.quit_application)

    def show_frame(self, name):
        self.current_page.destroy()
        self.current_page = name(parent=self.main_frame, app=self)
        self.current_page.place(rely=0, relx=0)
        self.current_page.tkraise()

    def show_about_window(self):
        about = AboutWindow()
        about.focus_set()
        about.grab_set()

    def show_calculations_window(self):
        calc_view = CalculationsWindow()
        calc_view.focus_set()
        calc_view.grab_set()

    def refresh_db_instruments(self):
        all_instruments = self.oanda_connection.get_instruments()
        saved_instruments = self.db.store_instruments(all_instruments)
        messagebox.showinfo(
            message=f"{saved_instruments} saved.", title="Database Refresh"
        )

    def set_connections(self, oanda_account, oanda_api, news_api, alpha_vantage_api):
        self.alphavantage_connection = AlphaVantageAPI(api_key=alpha_vantage_api)
        self.news_connection = NewsConnection(news_api)
        self.oanda_connection = OandaConnection(
            account_id=oanda_account, api_key=oanda_api
        )
        self.show_frame(HomePage)

    def quit_application(self):
        if messagebox.askyesno("Exit", "Do you want to quit the application?"):
            self.destroy()


if __name__ == "__main__":
    root = Application()
    root.withdraw()
    root.mainloop()
