import tkinter as tk
from tkinter import ttk
from ..basepage import BasePage


class OrderPage(BasePage):
    def __init__(self, parent, app):
        super().__init__(parent)
        frame_order = tk.LabelFrame(self, self.frame_styles,
                                    text="Create an Order")
        frame_order.place(rely=0.03, relx=0.02, height=150, width=300)
