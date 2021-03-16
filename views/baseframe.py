import tkinter as tk


class BaseFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        base_frame = tk.Frame(self, bg="#94b4d1", height=600, width=1024)
        base_frame.pack(fill="both", expand="true")

        self.frame_styles = {"relief": "groove", "bd": 3, "bg": "#94b4d1",
                             "fg": "#073bb3", "font": ("Arial", 9, "bold")}
