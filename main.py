import tkinter as tk
import os
import custom_objects
from navigation import Navbar
from views import HomePage, AboutWindow, CalculationsWindow

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

    def quit_application(self):
        self.destroy()


if __name__ == "__main__":
    root = Application()
    #root.withdraw()
    root.mainloop()
