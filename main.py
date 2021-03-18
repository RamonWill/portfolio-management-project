import tkinter as tk
from tkinter import messagebox
from navigation import Navbar
from views import HomePage, AboutWindow, CalculationsWindow
from external_connections import NewsConnection, AlphaVantageAPI, OandaConnection
from models import PRMS_Database
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
        self.alphavantage_connection = AlphaVantageAPI(api_key="UHJKNP33E9D8KCRS")
        self.news_connection = NewsConnection("3fd4076c2a15490ca9a979cd52429448")
        self.oanda_connection  = OandaConnection(account_id="101-004-18515982-001", api_key="96732e2978c2339ada31ef16971308fd-5ef54f7a26646a169d04a02befb786ca")
        self.current_page = tk.Frame()
        self.show_frame(HomePage)
        menubar = Navbar(root=self)
        tk.Tk.config(self, menu=menubar)

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
        messagebox.showinfo(message=f"{saved_instruments} saved.", title="Database Refresh")
    def quit_application(self):
        self.destroy()


if __name__ == "__main__":
    root = Application()
    authenticator = None  # This will be the login/register tasks might need to communicate with the application so maybe
    # make the application withdraw itself? login then if successful update the apis from the db..
    #root.withdraw()
    root.mainloop()

