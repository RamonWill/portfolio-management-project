import tkinter as tk
import os
from navigation import Navbar
from views import *

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
        self.view_container = {}

        for page in VIEW_PAGES:
            frame = page(parent=self.main_frame, app=self)
            self.view_container[page] = frame
            frame.place(rely=0, relx=0)
        self.show_frame(VIEW_PAGES[0])

        menubar = Navbar(root=self)
        tk.Tk.config(self, menu=menubar)

    def show_frame(self, name):
        frame = self.view_container[name]
        frame.tkraise()

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
