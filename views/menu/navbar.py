import tkinter as tk


class Navbar(tk.Menu):
    def __init__(self, root):
        super().__init__(root)

        menu_styles = {"tearoff": 0, "bd": 5, "activebackground": "#d9d9d9",
                       "background": "#FFFFFF", "activeforeground": "#000000"}

        # File
        menu_file = tk.Menu(self, menu_styles)
        self.add_cascade(label="File", menu=menu_file)
        menu_file.add_command(label="Homepage")
        menu_file.add_separator()
        menu_file.add_command(label="Exit",
                              command=root.quit_application)

        # Market Orders
        menu_orders = tk.Menu(self, menu_styles)
        self.add_cascade(label="Market Orders", menu=menu_orders)
        menu_orders.add_command(label="Create Buy/Sell Order")
        menu_orders.add_separator()
        menu_orders.add_command(label="FX Algo Trading")

        # FX Pricing
        menu_pricing = tk.Menu(self, menu_styles)
        self.add_cascade(label="FX Pricing", menu=menu_pricing)
        menu_pricing.add_command(label="FX Prices/Charts")

        # Operations
        menu_operations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Operations", menu=menu_operations)
        menu_operations.add_command(label="Trade Bookings")
        # Operations - Positions
        menu_positions = tk.Menu(menu_operations, menu_styles)
        menu_operations.add_cascade(label="Positions", menu=menu_positions)
        menu_positions.add_command(label="View Positions")
        menu_positions.add_command(label="Position Reconciliation")

        # Tools/Calculators
        menu_calculations = tk.Menu(self, menu_styles)
        self.add_cascade(label="Tools/Calculators", menu=menu_calculations)
        menu_calculations.add_command(label="32nds/Decimal Converter")
        menu_calculations.add_command(label="Refresh database instruments...")

        # Help
        menu_help = tk.Menu(self, menu_styles)
        self.add_cascade(label="Help", menu=menu_help)
        menu_help.add_command(label="About...", command=root.show_about_window)
