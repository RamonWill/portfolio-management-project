import tkinter as tk
from . import views

class NavBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)

        menu_styles = {"tearoff": 0, "bd": 5,
                       "activebackground": "#d9d9d9",
                       "background": "#FFFFFF",
                       "activeforeground": "#000000"}

        menu_file = tk.Menu(self, menu_styles)
        self.add_cascade(label="File", menu=menu_file)
        menu_file.add_command(label="Homepage", command=lambda: parent.show_frame(views.HomePageFrame))
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=lambda: parent.Quit_application())

        menu_orders = tk.Menu(self, menu_styles)
        self.add_cascade(label="Market Orders", menu=menu_orders)
        menu_orders.add_command(label="Create Buy/Sell Order", command=lambda: parent.show_frame(views.CreateOrdersFrame))
        menu_orders.add_separator()
        menu_orders.add_command(label="FX Algo Trading", command=lambda: parent.show_frame(views.AlgoTradingFrame))

        menu_pricing = tk.Menu(self, menu_styles)
        self.add_cascade(label="FX Pricing", menu=menu_pricing)
        menu_pricing.add_command(label="FX Prices/Charts", command=lambda: parent.show_frame(views.SecurityPricesFrame))

        menu_operations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Operations", menu=menu_operations)
        menu_operations.add_command(label="Trade Bookings", command=lambda: parent.show_frame(views.TradeBookingsFrame))
        menu_positions = tk.Menu(menu_operations, menu_styles)
        menu_operations.add_cascade(label="Positions", menu=menu_positions)
        menu_positions.add_command(label="View Positions", command=lambda: parent.show_frame(views.CurrentPositionsFrame))
        menu_positions.add_command(label="Position Reconciliation", command=lambda: parent.show_frame(views.PositionRecFrame))

        menu_calculations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Tools/Calculators", menu=menu_calculations)
        menu_calculations.add_command(label="32nds/Decimal Converter", command=lambda: parent.Get_treasurypage())
        menu_calculations.add_command(label="Refresh database instruments...", command=lambda: parent.update_instrument_db())

        menu_help = tk.Menu(self, menu_styles)
        self.add_cascade(label="Help", menu=menu_help)
        menu_help.add_command(label="About...", command=lambda: parent.AboutMe())
