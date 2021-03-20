import tkinter as tk


class BaseWindow(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.base_frame = tk.Frame(self)
        self.base_frame.pack(fill="both", expand="true")
        self.base_frame.pack_propagate(0)

        self.frame_styles = {
            "relief": "groove",
            "bd": 3,
            "bg": "#94b4d1",
            "fg": "#073bb3",
            "font": ("Arial", 9, "bold"),
        }

        self.text_styles = {
            "font": ("Verdana", 10),
            "background": "#3F6BAA",
            "foreground": "#E1FFFF",
        }
