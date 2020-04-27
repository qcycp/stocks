import sqlite3
import time
import traceback
import app.constants as CONST
from app.foundation import logger

class DB_Utils(object):
    def __init__(self):
        self.conn = sqlite3.connect(CONST.DB_FILE)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        self.commit()

        self.init_table_stock()
        self.init_table_daily()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def init_table_stock(self):
        try:
            sql = '''CREATE TABLE IF NOT EXISTS stock (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     code TEXT NOT NULL UNIQUE,
                     name TEXT NOT NULL UNIQUE,
                     listed_day TEXT NOT NULL,
                     listed_type INTEGER NOT NULL,
                     CFICode TEXT NOT NULL,
                     listed BOOLEAN DEFAULT True
                     );'''
            self.cursor.execute(sql)

            sql = ("CREATE INDEX IF NOT EXISTS index_stock_code ON stock (code);")
            self.cursor.execute(sql)

            sql = ("CREATE INDEX IF NOT EXISTS index_stock_name ON stock (name);")
            self.cursor.execute(sql)

            self.commit()
        except:
            logger.error(traceback.format_exc())

    def init_table_daily(self):
        try:
            #日期 開盤價 最高價 最低價 收盤價 成交股數
            sql = '''CREATE TABLE IF NOT EXISTS daily (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date TEXT NOT NULL,
                     code TEXT NOT NULL,
                     name TEXT NOT NULL,
                     open REAL,
                     high REAL,
                     low REAL,
                     close REAL,
                     volume REAL NOT NULL,
                     stock_id INTEGER,
                     UNIQUE(date, code),
                     FOREIGN KEY(stock_id) REFERENCES stock(id) ON DELETE CASCADE
                     );'''
            self.cursor.execute(sql)
            self.commit()
        except:
            logger.error(traceback.format_exc())

#cursor.execute("SELECT * FROM {} WHERE code=?".format(stock), ('2330',))
#cursor.execute("INSERT INTO {} VALUES(?, ?)".format(group), ('台積電', '2330'))
#cursor.execute("UPDATE {} SET alive=? WHERE code=?".format(group), (False, '2330'))
#cursor.execute("SELECT * FROM stock INNER JOIN daily ON stock.id = daily.stock_id WHERE stock.code = '2330';")
#cursor.execute("DELETE from stock where id=1")