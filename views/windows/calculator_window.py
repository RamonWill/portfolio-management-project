import tkinter as tk
from tkinter import ttk
from presenters import CalculationsPresenter
from .basewindow import BaseWindow


class CalculationsWindow(BaseWindow):
    def __init__(self):
        super().__init__()

        self.geometry("300x200")
        self.resizable(0, 0)

        self.title("T-Bill Conversion")

        self.presenter = CalculationsPresenter(view=self)

        frame1 = tk.LabelFrame(
            self.base_frame,
            self.frame_styles,
            text="Enter the price you want to convert",
        )
        frame1.pack(expand=True, fill="both")

        label = tk.Label(
            frame1, text="Enter price here: ", font=("Trebuchet MS", 9), bg="#94b4d1"
        )
        label.place(rely=0.05, relx=0.05)

        self.entry1 = ttk.Entry(frame1, width=7, cursor="xterm")
        self.entry1.place(rely=0.05, relx=0.50)

        self.label2 = tk.Label(frame1)
        self.label2.place(rely=0.4, relx=0.3, height=75, width=150)

        btn_convert = ttk.Button(
            frame1, text="Convert price", command=lambda: self.initiate_conversion()
        )
        btn_convert.place(rely=0.20, relx=0.50)

    def initiate_conversion(self):
        price = self.entry1.get()
        self.presenter.convert_price(price=price)

    def display_conversion(self, new_price):
        self.label2.configure(text=new_price)
