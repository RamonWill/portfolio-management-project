import sqlite3
import pandas as pd
from pathlib import Path

PARENT_PATH = Path(__file__).parent.parent

# r"C:\Users\Owner\Documents\PRMS_API\source.db"


class PRMS_Database(object):
    def __init__(self):

        __DB_PATH = str(Path.joinpath(PARENT_PATH, "source.db"))
        self.conn = sqlite3.connect(__DB_PATH)
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

    def updates_instruments(self, name, display_name):
        """
        Stores instruments from the Oanda platform to the source database if
        they do not already exist in the database.
        """
        query = """INSERT INTO Instruments
                   VALUES (:name, :displayName);"""
        self.cur.execute(query, {"name": name, "displayName": display_name})
        # The above might work. test it out

    def get_largest_positions(self):
        query = """SELECT name, SUM(quantity*price) as 'MarketVal'
                    FROM All_Transactions
                    WHERE cancelled = 0
                    GROUP BY name
                    ORDER BY ABS(SUM(quantity*price))DESC
                    LIMIT 5;"""
        positions = pd.read_sql_query(query, self.conn)
        return positions

    def get_all_positions(self):
        query = """SELECT *
                   FROM All_Transactions;"""
        all_positions = pd.read_sql_query(query, self.conn)
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

    def add_to_db(self, instrument, units, price, id=None, profit=0):
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
        # This query can be improved. previous query average wasn't weighted.
        # here i weight short trades vs long then average them both together,
        query = """SELECT
                    Instrument,
                    SUM([Units]) as 'PRMS Units',
                    AVG([Price]) as 'PRMS Avg Price'
                FROM
                (
                    SELECT
                        a.name as 'Instrument',
                        CASE WHEN a.quantity < 0 then SUM(a.quantity) else 0 end as 'Units',
                        CASE WHEN a.quantity < 0 then SUM(a.quantity*a.price)/SUM(a.quantity) else 0 end as 'Price'
                        from All_Transactions a
                    WHERE a.cancelled = 0 AND a.quantity < 0
                    GROUP BY a.name
                    HAVING 'Price' > 0

                    UNION ALL

                    SELECT
                        b.name as 'Instrument',
                        CASE WHEN b.quantity > 0 then SUM(b.quantity) else 0 end as 'Units',
                        CASE WHEN b.quantity > 0 then SUM(b.quantity*b.price)/SUM(b.quantity) else 0 end as 'Price'
                        FROM All_Transactions b
                    WHERE b.cancelled = 0 AND b.quantity > 0
                    GROUP BY b.name
                    HAVING 'Price' > 0)
                GROUP BY Instrument """

        prms_positions = pd.read_sql_query(query, self.conn)

        return prms_positions

# Login and Register
    def validate_entry(self, name, quantity, price):

        instruments = self.get_db_instruments()

        try:
            p = next(True for key, value in instruments.items() if value == name)
            quantity = float(quantity)
            check_price = (float(price) >= 0)
        except (StopIteration, ValueError) as e:
            if (isinstance(e, StopIteration)):
                return "The name you have entered is not a tradeable instrument."
            elif(isinstance(e, ValueError)):
                return "The Quantity and Price must be valid numbers."

        if not check_price:
            return "The Price cannot be a negative number"
        else:
            return True

    def Validate_login(self, username, password):

        self.cur.execute("""SELECT Username, Password
                     FROM LoginInfo
                     WHERE Username=? AND Password=?""", (username, password,))
        login_check = self.cur.fetchone()
        try:
            validation = len(login_check)
            return (validation == 2)

        except TypeError:
            return False

    def registration(self, username, password):
        self.cur.execute("""SELECT Username
                            FROM LoginInfo
                            WHERE Username=?""", (username,))
        username_check = self.cur.fetchone()
        if username_check is None:
            self.store_credentials(username, password)
            return True
        else:
            return "The Username you have entered already exists."

    def store_credentials(self, username, password):
        query = """INSERT INTO LoginInfo
                   VALUES (:Username, :Password)"""
        self.cur.execute(query, {"Username": username, "Password": password})
