import os

APPDIR = os.path.abspath(os.path.dirname(__file__))
UPDATE_FILE = os.path.join(APPDIR, '..', 'data', 'update')
DB_FILE = os.path.join(APPDIR, '..', 'data', 'data.db')

URL_TYPE_LISTED_COMPANY = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
URL_TYPE_OTC_COMPANY = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
URL_TYPE_EMERGING_STOCK_COMPANY = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=5"

#每日收盤行情，自民國93年2月11日起提供
#https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html
#https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=20040211&type=ALLBUT0999

VALID_LISTED_TYPE = ['上市', '上櫃', '興櫃']

class LISTED_TYPE:
    TYPE_LISTED_COMPANY = 0
    TYPE_OTC_COMPANY = 1
    TYPE_EMERGING_STOCK_COMPANY = 2

    state_mapping = {
        TYPE_LISTED_COMPANY: "上市",
        TYPE_OTC_COMPANY: "上櫃",
        TYPE_EMERGING_STOCK_COMPANY: "興櫃"
    }

    state_mapping_reverse = {
        "上市": TYPE_LISTED_COMPANY,
        "上櫃": TYPE_OTC_COMPANY,
        "興櫃": TYPE_EMERGING_STOCK_COMPANY
    }