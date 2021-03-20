import tkinter as tk
from views import *
from custom_objects import Callback


class Navbar(tk.Menu):
    def __init__(self, root):
        super().__init__(root)

        menu_styles = {
            "tearoff": 0,
            "bd": 5,
            "activebackground": "#d9d9d9",
            "background": "#FFFFFF",
            "activeforeground": "#000000",
        }

        # File
        menu_file = tk.Menu(self, menu_styles)
        self.add_cascade(label="File", menu=menu_file)
        menu_file.add_command(
            label="Homepage", command=Callback(root.show_frame, HomePage)
        )
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=root.quit_application)

        # Market Orders
        menu_orders = tk.Menu(self, menu_styles)
        self.add_cascade(label="Market Orders", menu=menu_orders)
        menu_orders.add_command(
            label="Create Buy/Sell Order", command=Callback(root.show_frame, OrderPage)
        )
        menu_orders.add_separator()
        menu_orders.add_command(label="FX Algo Trading")

        # FX Pricing
        menu_pricing = tk.Menu(self, menu_styles)
        self.add_cascade(label="FX Pricing", menu=menu_pricing)
        menu_pricing.add_command(
            label="FX Prices/Charts", command=Callback(root.show_frame, PricesPage)
        )

        # Operations
        menu_operations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Operations", menu=menu_operations)
        menu_operations.add_command(
            label="Trade Bookings", command=Callback(root.show_frame, TradeBookingsPage)
        )
        # Operations - Positions
        menu_positions = tk.Menu(menu_operations, menu_styles)
        menu_operations.add_cascade(label="Positions", menu=menu_positions)
        menu_positions.add_command(
            label="View Positions", command=Callback(root.show_frame, PositionsPage)
        )
        menu_positions.add_command(
            label="Position Reconciliation",
            command=Callback(root.show_frame, PositionsRecPage),
        )

        # Tools/Calculators
        menu_calculations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Tools/Calculators", menu=menu_calculations)
        menu_calculations.add_command(
            label="32nds/Decimal Converter", command=root.show_calculations_window
        )
        menu_calculations.add_command(
            label="Refresh database instruments...", command=root.refresh_db_instruments
        )

        # Help
        menu_help = tk.Menu(self, menu_styles)
        self.add_cascade(label="Help", menu=menu_help)
        menu_help.add_command(label="About...", command=root.show_about_window)
