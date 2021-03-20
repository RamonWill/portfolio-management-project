from tkinter import messagebox


class TradeBookingsPresenter(object):
    def __init__(self, view, db):
        self.view = view
        self._db = db

    def set_transaction_status(self, id, toggle):
        toggle_status = self._db.cancelled_toggle(id=id, toggle=toggle)
        messagebox.showinfo(message=toggle_status, title="Transaction Status")
        self.view.clear_status_entries()

    def get_transactions(self):
        db_transactions = self._db.get_transactions()
        self.view.display_transactions(transactions=db_transactions)

    def store_transaction(self, name, quantity, price):
        try:
            q = float(quantity)
            p = float(price)
        except ValueError:
            messagebox.showerror(
                message="invalid price or quantity", title="Invalid Entry"
            )
            return None
        if float(price) < 0:
            messagebox.showerror(
                message="the price cannot be a negative number", title="Invalid Entry"
            )
            return None
        status = self._db.save_transaction(name, quantity, price)
        messagebox.showinfo(message=status, title="Transactions Saved")
        self.get_transactions()
