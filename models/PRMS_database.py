import sqlite3
from pathlib import Path

class DBContext(object):
    def __init__(self, db_file=""):
        self.db_file = db_file
        self.connection_status = Path(db_file).exists()

    def __enter__(self):
        self.conn= sqlite3.connect(self.db_file)
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
            self.context.connection_status=True
        self.is_connected = self.context.connection_status

    def get_db_instruments(self):
        """ Extracts a list of all instruments from the source database."""
        with self.context as db:
            db.execute("""SELECT name, displayName
                                FROM Instruments
                                ORDER BY displayName;""")
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
                    db.execute(insert_query, {"name":name, "displayName":display_name})
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
                    values = {"id":id,"name":instrument,"quantity":units,"price":price,"profit":profit, "cancelled":cancelled}
                    insert_query = "INSERT INTO All_Transactions VALUES (:id, :name, :quantity, :price, :profit, :cancelled);"
                    db.execute(insert_query, values)


    def _setup_database_tables(self):
        "Creates tables for the Database"
        with self.context as db:
            db.execute("CREATE TABLE IF NOT EXISTS LoginInfo \
                         (username TEXT, password TEXT, oanda_api TEXT, oanda_account TEXT, news_api TEXT, alphaVantage_api TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS Instruments\
                         (name TEXT, displayName TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS All_Transactions\
                         (id TEXT, name TEXT, quantity REAL, price REAL, pnl REAL, cancelled INTEGER)")

        print(f"A new database has been created in {self.DB_PATH}")

    def get_credentials(self):
        # I need to check the user first. so authenticator will need to be done first
        with self.context as db:
            db.execute("SELECT oanda_api, oanda_account, news_api, alphaVantage_api\
                        FROM LoginInfo;")
            credentials = db.fetchall()
        return credentials