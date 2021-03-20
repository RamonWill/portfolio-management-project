import tkinter as tk


class BasePage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.base_frame = tk.Frame(self, bg="#94b4d1", height=600, width=1024)
        self.base_frame.pack(fill="both", expand="true")

        self.frame_styles = {
            "relief": "groove",
            "bd": 3,
            "bg": "#94b4d1",
            "fg": "#073bb3",
            "font": ("Arial", 9, "bold"),
        }

        self.text_styles = {"bg": "#94b4d1", "font": ("Verdana", 9)}
