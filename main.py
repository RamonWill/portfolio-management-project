import tkinter as tk
import os
from views import Navbar, AboutWindow, CalculationsWindow
# Portfolio Reconciliation and Management System (PRMS)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PRMSystem")
        main_frame = tk.Frame(self, bg="#84CEEB")
        main_frame.pack(fill="both", expand="true")
        main_frame.pack_propagate(0)
        self.geometry("1024x600")
        self.view_container = {}
        pages = ()

        for page in pages:
            frame = page(parent=main_frame, app=self)
            self.frames[page] = frame
            frame.place(rely=0, relx=0)
            frame.tkraise()
        #self.show_frame()

        menubar = Navbar(root=self)
        tk.Tk.config(self, menu=menubar)

    def show_frame(self, name):
        frame = self.frames[name]
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
