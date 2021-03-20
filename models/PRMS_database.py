import sqlite3
from pathlib import Path
from collections import namedtuple


class DBContext(object):
    def __init__(self, db_file=""):
        self.db_file = db_file
        self.connection_status = Path(db_file).exists()

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, ext_type, exc_value, traceback):
        self.cur.close()

        if isinstance(exc_value, Exception):  # Exception occured rollback
            self.conn.rollback()
            print("An error occured. Changes rolled back")
        else:
            self.conn.commit()
        self.conn.close()


class PRMS_Database(object):
    def __init__(self):
        _DATABASE_NAME = "prms_database.db"
        _PARENT_PATH = Path(__file__).parent.parent

        self.DB_PATH = str(Path.joinpath(_PARENT_PATH, _DATABASE_NAME))
        self.context = DBContext(self.DB_PATH)

        if not self.context.connection_status:
            self._setup_database_tables()
            self.context.connection_status = True
        self.is_connected = self.context.connection_status

    def get_db_instruments(self):
        """ Extracts a list of all instruments from the source database."""
        with self.context as db:
            db.execute(
                """SELECT name, displayName
                                FROM Instruments
                                ORDER BY displayName;"""
            )
            instrument_table = db.fetchall()
        instrument_pairs = {row["name"]: row["displayName"] for row in instrument_table}
        return instrument_pairs

    def store_instruments(self, oanda_instruments):
        db_instruments = self.get_db_instruments()
        db_names = set(db_instruments.keys())
        count = 0
        insert_query = "INSERT INTO Instruments VALUES (:name, :displayName);"
        with self.context as db:
            for name, display_name in oanda_instruments.items():
                if name not in db_names:
                    db.execute(
                        insert_query, {"name": name, "displayName": display_name}
                    )
                    count += 1
        return count

    def record_trade(self, fill):
        if not isinstance(fill, str):
            if "orderFillTransaction" in fill:
                id = fill["orderFillTransaction"]["orderID"]
                instrument = fill["orderFillTransaction"]["instrument"]
                units = fill["orderFillTransaction"]["units"]
                price = fill["orderFillTransaction"]["price"]
                profit = fill["orderFillTransaction"]["pl"]
                cancelled = 0
                with self.context as db:
                    values = {
                        "id": id,
                        "name": instrument,
                        "quantity": units,
                        "price": price,
                        "profit": profit,
                        "cancelled": cancelled,
                    }
                    insert_query = "INSERT INTO All_Transactions VALUES (:id, :name, :quantity, :price, :profit, :cancelled);"
                    db.execute(insert_query, values)

    def _setup_database_tables(self):
        "Creates tables for the Database"
        with self.context as db:
            db.execute(
                "CREATE TABLE IF NOT EXISTS LoginInfo \
                         (username TEXT, salt BLOB, key BLOB, oanda_api TEXT, oanda_account TEXT, news_api TEXT, alphaVantage_api TEXT)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS Instruments\
                         (name TEXT, displayName TEXT)"
            )
            db.execute(
                "CREATE TABLE IF NOT EXISTS All_Transactions\
                         (id TEXT, name TEXT, quantity REAL, price REAL, pnl REAL, cancelled INTEGER)"
            )

        print(f"A new database has been created in {self.DB_PATH}")

    def get_transactions(self):
        query = "SELECT * FROM All_Transactions;"
        with self.context as db:
            db.execute(query)
            result = db.fetchall()
        transactions = []
        for row in result:
            t = DBTransaction(
                id=row["id"],
                name=row["name"],
                quantity=row["quantity"],
                price=row["price"],
                pnl=row["pnl"],
                cancelled=row["cancelled"],
            )
            transactions.append(t)

        return transactions

    def cancelled_toggle(self, id, toggle):
        with self.context as db:
            db.execute(
                """UPDATE all_Transactions
                            SET cancelled = ?
                            WHERE id = ?""",
                (toggle, id),
            )
            result = db.rowcount
        if result == 0:
            return "Order ID does not exist in the database."
        else:
            return f"Changes have been made to Order ID {id}."

    def get_credentials(self):
        # I need to check the user first. so authenticator will need to be done first
        with self.context as db:
            db.execute(
                "SELECT oanda_api, oanda_account, news_api, alphaVantage_api\
                        FROM LoginInfo;"
            )
            credentials = db.fetchall()
        return credentials

    def _generateId(self):
        with self.context as db:
            db.execute(
                """SELECT MAX(TRIM(id, 'C'))
                              FROM all_transactions
                              WHERE id LIKE 'C%' """
            )
            last_id = db.fetchone()[0]

        if last_id is None:
            new_id = "C{:04n}".format(1)
        else:
            new_id = "C{:04n}".format(int(last_id) + 1)

        return new_id

    def save_transaction(self, name, units, price):

        id = self._generateId()

        placeholders = {
            "id": id,
            "name": name,
            "quantity": units,
            "price": price,
            "pnl": 0,
            "cancelled": 0,
        }
        with self.context as db:
            db.execute(
                """INSERT INTO All_Transactions
                                VALUES (:id, :name, :quantity, :price, :pnl, :cancelled)""",
                placeholders,
            )
        return f"Order ID {id} stored to the database"

    def get_db_positions(self):
        # This query can be improved. previous query average wasn't weighted.
        # here i weight short trades vs long then average them both together,
        query = """SELECT
                    Instrument as 'name',
                    SUM([Units]) as 'prms_units',
                    AVG([Price]) as 'prms_avg_price'
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

        with self.context as db:
            db.execute(query)
            db_positions = db.fetchall()
        prms_positions = []
        for position in db_positions:
            p = DBPosition(
                position["name"], position["prms_units"], position["prms_avg_price"]
            )
            prms_positions.append(p)
        return prms_positions

    def get_largest_positions(self):
        query = """SELECT name, SUM(quantity*price) as 'MarketVal'
                    FROM All_Transactions
                    WHERE cancelled = 0
                    GROUP BY name
                    ORDER BY ABS(SUM(quantity*price))DESC
                    LIMIT 5;"""
        with self.context as db:
            db.execute(query)
            db_positions = db.fetchall()
        positions = [
            DBPieChartData(row["name"], row["MarketVal"]) for row in db_positions
        ]
        return positions

    def validate_registration(self, username):
        # check if username already exists
        with self.context as db:
            query = "SELECT Username FROM LoginInfo WHERE Username=?"
            db.execute(query, (username,))
            user = db.fetchone()
        is_valid = user is None
        return is_valid

    def store_user_credentials(
        self, username, hash, oanda_account, oanda_api, news_api, alpha_vantage_api
    ):
        with self.context as db:
            query = "INSERT INTO LoginInfo VALUES (:username, :key, :salt, :oanda_api, :oanda_account, :news_api, :alphaVantage_api)"
            values = {
                "username": username,
                "key": hash["key"],
                "salt": hash["salt"],
                "oanda_account": oanda_account,
                "oanda_api": oanda_api,
                "news_api": news_api,
                "alphaVantage_api": alpha_vantage_api,
            }
            db.execute(query, values)

    def get_user(self, username):
        with self.context as db:
            query = "SELECT * FROM LoginInfo WHERE username=?"
            db.execute(query, (username,))
            db_user = db.fetchone()
        if db_user is None:
            return None
        else:
            user = DBUser(
                db_user["username"],
                db_user["key"],
                db_user["salt"],
                db_user["oanda_account"],
                db_user["oanda_api"],
                db_user["news_api"],
                db_user["alphaVantage_api"],
            )
            return user


class DBObject(object):
    pass


class DBTransaction(DBObject):
    def __init__(self, id, name, quantity, price, pnl, cancelled):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.price = price
        self.pnl = pnl
        self.cancelled = cancelled


class DBPosition(DBObject):
    def __init__(self, name, prms_units, prms_avg_price):
        self.name = name
        self.prms_units = round(prms_units, 2)
        self.prms_avg_price = round(prms_avg_price, 2)


class DBPieChartData(DBObject):
    def __init__(self, name, MarketVal):
        self.name = name
        self.MarketVal = round(MarketVal, 2)


class DBUser(DBObject):
    def __init__(
        self, username, key, salt, oanda_account, oanda_api, news_api, alpha_vantage_api
    ):
        self.username = username
        self.key = key
        self.salt = salt
        self.oanda_account = oanda_account
        self.oanda_api = oanda_api
        self.news_api = news_api
        self.alpha_vantage_api = alpha_vantage_api
