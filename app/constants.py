import os
from config import DATADIR

UPDATE_FILE = os.path.join(DATADIR, 'update')
DB_FILE = os.path.join(DATADIR, 'data.db')
STOCK_LIST = os.path.join(DATADIR, 'stock_list')

CURRENT_YEAR = 2020

URL_TYPE_LISTED_COMPANY = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
URL_TYPE_OTC_COMPANY = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
URL_TYPE_EMERGING_STOCK_COMPANY = "http://isin.twse.com.tw/isin/C_public.jsp?strMode=5"
GOODINFO_URL = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID="

#每日收盤行情，自民國93年2月11日起提供
#https://www.twse.com.tw/zh/page/trading/exchange/MI_INDEX.html
#https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=20040211&type=ALLBUT0999

VALID_LISTED_TYPE = ['上市', '上櫃', '興櫃']
VALID_CFICode = ['ESVUFR', 'ESVTFR', 'CEOGBU', 'CEOGCU', 'CEOGDU', 'CEOGEU', 'CEOGMU', 'CEOIBU', 'CEOIEU', 'CEOIRU', 'CEOJEU', 'CEOJLU']

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