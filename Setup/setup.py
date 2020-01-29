import sqlite3

# Set up Database Tables


def Setup_database_tables(path):
    conn = sqlite3.connect(path)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS LoginInfo
                 (Username TEXT, Password TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS Instruments
                 (name TEXT, displayName TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS All_Transactions
                 (id TEXT, name TEXT, quantity REAL, price REAL, pnl REAL, cancelled INTEGER)""")
    conn.commit()
    c.close()
    conn.close()
    return "A new database has been created in {}".format(path)
