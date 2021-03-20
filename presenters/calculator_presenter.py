from custom_objects import FinanceCalculator
from tkinter import messagebox


class CalculationsPresenter(object):
    def __init__(self, view):
        self.view = view

    def convert_price(self, price):
        try:
            converted_price = FinanceCalculator.decimal_to_treasury(price)
            self.view.display_conversion(new_price=converted_price)
            return None
        except (ValueError, IndexError) as err:
            pass
        try:
            converted_price = FinanceCalculator.treasury_to_decimal(price)
            self.view.display_conversion(new_price=converted_price)
        except (ValueError, IndexError) as err:
            messagebox.showinfo(
                message="An example of a valid price would be 108.50 or 108-16",
                title="Invalid Price",
            )
