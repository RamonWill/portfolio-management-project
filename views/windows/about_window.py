import tkinter as tk
from .basewindow import BaseWindow


class AboutWindow(BaseWindow):
    def __init__(self):
        super().__init__()

        self.geometry("500x500")
        self.resizable(0, 0)

        self.title("About")
        bio = """PRMSystem is a portfolio management project created by\n
        Ramon Williams. PRMSystem utilises the APIs from AlphaVantage, Oanda\n
        and NewsAPI to create interface that allows the user to read news\n
        articles, check FX prices/charts, execute trades and trade based\n
        on two algorithms. This project also allows you to perform\n
        position reconciliations and store Oanda trades into a database\n
        where ALL entries are logged.
        As I am learning more about software development this project has\n
        improved my knowledge on a variety of python libraries, APIs and SQL\n
        it has also been very helpful on increasing my understanding of\n
        Functions and OOP."""
        frame1 = tk.LabelFrame(
            self.base_frame, self.frame_styles, text="Thank you for viewing"
        )
        frame1.pack(expand=True, fill="both")

        label = tk.Label(frame1, text=bio, font=("Trebuchet MS", 9), bg="#94b4d1")
        label.pack(expand=True)
