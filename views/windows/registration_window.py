import tkinter as tk
from tkinter import ttk, messagebox
from .basewindow import BaseWindow


class RegistrationWindow(tk.Toplevel):
    def __init__(self, authenticator):
        super().__init__()
        self.authenticator = authenticator

        text_styles = {
            "font": ("Verdana", 10),
            "background": "#3F6BAA",
            "foreground": "#E1FFFF",
        }

        main_frame = tk.Frame(self, bg="#3F6BAA", height=150, width=250)
        # pack_propagate prevents the window resizing to match the widgets
        main_frame.pack_propagate(0)
        main_frame.pack(fill="both", expand="true")

        self.Presenter = None  # p.RegistrationPage(view=self)

        self.geometry("250x450")
        self.resizable(0, 0)
        self.title("Registration")
        label_user = tk.Label(main_frame, text_styles, text="New Username:")
        label_user.grid(row=1, column=0)
        self.entry_user = ttk.Entry(main_frame, width=20, cursor="xterm")
        self.entry_user.grid(row=1, column=1)

        label_pw = tk.Label(main_frame, text_styles, text="New Password:")
        label_pw.grid(row=2, column=0)
        self.entry_pw = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        self.entry_pw.grid(row=2, column=1)

        label_news_api = tk.Label(main_frame, text_styles, text="NewsAPI Api:")
        label_news_api.grid(row=3, column=0)
        self.entry_news_api = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        self.entry_news_api.grid(row=3, column=1)

        label_av = tk.Label(main_frame, text_styles, text="AlphaVantage Api:")
        label_av.grid(row=4, column=0)
        self.entry_av = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        self.entry_av.grid(row=4, column=1)

        label_oanda_acc = tk.Label(main_frame, text_styles, text="Oanda Account:")
        label_oanda_acc.grid(row=5, column=0)
        self.entry_oanda_acc = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        self.entry_oanda_acc.grid(row=5, column=1)

        label_oanda_api = tk.Label(main_frame, text_styles, text="Oanda Api:")
        label_oanda_api.grid(row=6, column=0)
        self.entry_oanda_api = ttk.Entry(main_frame, width=20, cursor="xterm", show="*")
        self.entry_oanda_api.grid(row=6, column=1)

        btn = ttk.Button(
            main_frame, text="Create Account", command=lambda: self.register()
        )
        btn.grid(row=7, column=1)

    def register(self):
        user = self.entry_user.get()
        pw = self.entry_pw.get()
        news = self.entry_news_api.get()
        oanda_acc = self.entry_oanda_acc.get()
        oanda_api = self.entry_oanda_api.get()
        alpha_vantage = self.entry_av.get()
        if user == "" or pw == "":
            messagebox.showinfo(
                title="Information", message="You must enter a username and password"
            )
        else:
            result = self.authenticator.register_user(
                user, pw, oanda_acc, oanda_api, news, alpha_vantage
            )
            if result:
                self.destroy()
