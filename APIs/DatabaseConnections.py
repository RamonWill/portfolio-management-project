import sqlite3
from pathlib import Path

PARENT_PATH = Path(__file__).parent.parent


class PRMS_Database(object):
    def __init__(self):

        __DB_PATH = str(Path.joinpath(PARENT_PATH, "source.db"))
        self.conn = sqlite3.connect(r"C:\Users\Owner\Documents\PRMS_API\source.db")
        self.cur = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.cur.close()
        if isinstance(exc_value, Exception):  # Exception occured rollback
            self.conn.rollback()
            print("An error occured. Changes rolled back")
        else:
            self.conn.commit()
        self.conn.close()

    def get_db_instruments(self):
        """ Extracts a list of all instruments from the source database."""
        self.conn.row_factory = sqlite3.Row

        self.cur.execute("""SELECT name, displayName
                     FROM Instruments
                     ORDER BY displayName;""")

        instrument_table = self.cur.fetchall()

        db_names = [row[0] for row in instrument_table]
        db_display_names = [row[1] for row in instrument_table]
        instrument_pairs = {name: display_name for name, display_name in
                            zip(db_names, db_display_names)}

        return instrument_pairs

    def load_instruments(self, names, display_names):
        """
        Stores instruments from the Oanda platform to the source database if
        they do not already exist in the database.
        """
        query = """INSERT INTO Instruments
                   VALUES (:name, :displayName);"""
        self.cur.execute(query, {"name": names, "displayName": display_names})
        # The above might work. test it out

    def get_largest_positions(self):
        query = """SELECT name, SUM(quantity*price) as 'MarketVal'
                    FROM All_Transactions
                    WHERE cancelled = 0
                    GROUP BY name
                    ORDER BY ABS(SUM(quantity*price))DESC
                    LIMIT 5;"""
        self.cur.execute(query)
        positions = self.cur.fetchall()
        return positions

    def get_all_positions(self):
        query = """SELECT *
                   FROM All_Transactions;"""
        self.cur.execute(query)
        all_positions = self.cur.fetchall()
        return all_positions

    def generateID(self):
        self.cur.execute("""SELECT MAX(TRIM(id, 'C'))
                          FROM all_transactions
                          WHERE id LIKE 'C%' """)
        last_id = self.cur.fetchone()[0]

        if last_id is None:
            new_id = "C{:04n}".format(1)
        else:
            new_id = "C{:04n}".format(int(last_id)+1)

        return new_id

    def cancelled_toggle(self, id, toggle):
        self.cur.execute("""UPDATE all_transactions
                     SET cancelled = ?
                     WHERE id = ?""", (toggle, id))

        result = self.cur.rowcount
        if result == 0:
            return "Order ID does not exist in the database.".format(id)
        else:
            return "Changes have been made to Order ID {}.".format(id)

    def add_to_db(self, instrument, units, price, id=None, cancelled=0, profit=0):
        if id is None:
            id = self.generateID()

        placeholders = {"id": id,
                        "name": instrument,
                        "quantity": units,
                        "price": price,
                        "pnl": profit,
                        "cancelled": 0
                        }
        self.cur.execute("""INSERT INTO All_Transactions
                     VALUES (:id, :name, :quantity, :price, :pnl, :cancelled)""",
                  placeholders)
        return "Order ID {} stored to the database".format(id)

    def get_prms_positions(self):

        self.conn.row_factory = sqlite3.Row
        query = """SELECT
                    name as "Instrument",
                    SUM(quantity) as "PRMS Units",
                    price as "PRMS Avg Price"
                   FROM All_transactions
                   WHERE cancelled = 0
                   GROUP BY name;"""

        self.cur.execute(query)
        rec_positions = self.cur.fetchall()

        return rec_positions
# Login and Register

        def Validate_login(self, username, password):

            self.cur.execute("""SELECT Username, Password
                         FROM LoginInfo
                         WHERE Username=? AND Password=?""", (username, password,))
            login_check = self.cur.fetchone()

            return len(login_check) == 1

        def signup(self, username, password, passcode):
            if passcode == "2019" and len(password) > 4:
                self.cur.execute("""SELECT Username
                             FROM LoginInfo
                             WHERE Username=?""", (username,))
                username_check = self.cur.fetchone()
                if username_check is None:
                    return True
                else:
                    return "The Username you have entered already exists."
            else:
                return "The Passcode you have entered is incorrect or\nyour password needs to be longer than 4 values."
