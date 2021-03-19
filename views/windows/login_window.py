import tkinter as tk
from tkinter import ttk
from .basewindow import BaseWindow
from .registration_window import RegistrationWindow

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, authenticator):
        super().__init__()
        self.root = parent
        self.authenticator = authenticator
        title_styles = {"font": ("Trebuchet MS Bold", 16),
                        "background": "#3F6BAA",
                        "foreground": "#E1FFFF",
                        "justify": "left"}

        text_styles = {"font": ("Verdana", 14),
                       "background": "#3F6BAA",
                       "foreground": "#E1FFFF"}

        main_frame = tk.Frame(self, bg="#708090", height=431, width=626)
        main_frame.pack(fill="both", expand="true")
        self.title("PRMSystem")
        self.geometry("626x431")  # Sets window size to 626w x 431h pixels
        self.resizable(0, 0)  # This prevents any resizing of the screen

        self.presenter = None

        self.background_image = tk.PhotoImage(file=r"Views\login_bg_img.png")
        background_label = tk.Label(main_frame, image=self.background_image)
        background_label.place(relwidth=1, relheight=1)

        frame_login = tk.Frame(main_frame, bg="#3F6BAA", relief="groove", bd=2)
        frame_login.place(rely=0.30, relx=0.17, height=130, width=400)

        label_title = tk.Label(frame_login, title_styles,
                               text="PRMSystem Login Page")
        label_title.grid(row=0, column=1, columnspan=1)
        label_user = tk.Label(frame_login, text_styles, text="Username:")
        label_user.grid(row=1, column=0)
        label_pw = tk.Label(frame_login, text_styles, text="Password:")
        label_pw.grid(row=2, column=0)

        self.entry_user = ttk.Entry(frame_login, width=45, cursor="xterm")
        self.entry_user.grid(row=1, column=1)
        self.entry_pw = ttk.Entry(frame_login, width=45, cursor="xterm",
                                  show="*")
        self.entry_pw.grid(row=2, column=1)

        btn = ttk.Button(frame_login, text="Login", style="btns.TButton",
                         command=self.login)
        btn.place(rely=0.70, relx=0.50)

        signup_btn = ttk.Button(frame_login, style="btns.TButton",
                                text="Register",
                                command=self.get_register)
        signup_btn.place(rely=0.70, relx=0.75)

        label_user = tk.Label(main_frame, font=("Arial Black", 8),
                              background="#3F6BAA",
                              text="Created by Ramon Williams")
        label_user.place(rely=0.9, relx=0.7)

        s = ttk.Style()
        s.configure("btns.TButton",
                    font=("Arial", 10, "bold"),
                    background="#74CAE3")

    def login(self):
        pass

    def get_register(self):
        RegistrationWindow(authenticator=self.authenticator)