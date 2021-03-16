import tkinter as tk
from tkinter import ttk
from ..basepage import BasePage


class HomePage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)
        frame_account = tk.LabelFrame(self, self.frame_styles,
                                      text="Account Details")
        frame_account.place(rely=0.05, relx=0.02, height=120, width=300)

        frame_prices = tk.LabelFrame(self, self.frame_styles,
                                     text="Tradable Securities")
        frame_prices.place(rely=0.30, relx=0.02, height=375, width=400)

        frame_news = tk.LabelFrame(self, self.frame_styles,
                                   text="Latest News Headlines")
        frame_news.place(rely=0.05, relx=0.45, height=280, width=550)
