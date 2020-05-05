import datetime
import json
import os
import requests
import time
import traceback
import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen

import app.constants as CONST
from app.after_hours import AfterHoursInfo
from app.api_utils import get
from app.constants import LISTED_TYPE
from app.foundation import logger
from globals import db, update

def add_stock(data):
    code = data[0].split()[0]

    db.cursor.execute("SELECT * FROM stock WHERE code=?", (code,))
    result = db.cursor.fetchone()
    if result is None:
        db.cursor.execute("INSERT INTO stock(code, name, listed_day, listed_type, CFICode) VALUES(?, ?, ?, ?, ?)", \
                          (data[0].split()[0],
                           data[0].split()[1],
                           data[2].replace('/', '-'),
                           LISTED_TYPE.state_mapping_reverse[data[3]],
                           data[5]))
        db.commit()

def update_listed_company(url):
    data = get(url)
    if data is not None:
        #get the first table
        df = pd.read_html(data)[0]
        #                       0                    1           2    3     4        5    6
        #0          有價證券代號及名稱  國際證券辨識號碼(ISIN Code)         上市日  市場別   產業別  CFICode   備註
        #1                 股票                   股票          股票   股票    股票       股票   股票
        #2            1101　台泥         TW0001101004  1962/02/09   上市  水泥工業   ESVUFR  NaN
        #3            1102　亞泥         TW0001102002  1962/06/08   上市  水泥工業   ESVUFR  NaN
        #df.columns: Int64Index([0, 1, 2, 3, 4, 5, 6], dtype='int64')
        
        #with open('test', 'a', encoding='UTF-8') as f:
        #    f.write(df.to_string(header = False, index = False))
        for index, row in df.iterrows():
            if row[3] in CONST.VALID_LISTED_TYPE:
                add_stock(row)
    else:
        logger.error(f"Cannot get data from {url}")

def update_stocks():
    #上次更新的日期
    last_update = update.data['stock']

    today = datetime.date.today().strftime('%Y%m%d')
    if last_update == today:
        logger.info("The data is up to date!!")
        return

    #上市
    logger.info("更新上市股票...")
    update_listed_company(CONST.URL_TYPE_LISTED_COMPANY)

    #上櫃
    logger.info("更新上櫃股票...")
    update_listed_company(CONST.URL_TYPE_OTC_COMPANY)

    #興櫃
    logger.info("更新興櫃股票...")
    update_listed_company(CONST.URL_TYPE_EMERGING_STOCK_COMPANY)

    update.update_stock_date()


def add_daily(date, info):
    db.cursor.execute(f"SELECT * FROM daily WHERE date='{date}' and code='{info.code}'")
    result = db.cursor.fetchone()
    if result != None:
        logger.error(f"The data is duplicated: {info}")
        return

    db.cursor.execute(f"SELECT id FROM stock WHERE code='{info.code}'")
    result = db.cursor.fetchone()
    if result != None:
        stock_id = result[0]
        if info.volume != 0:
            db.cursor.execute("INSERT INTO daily(date, code, name, open, high, low, close, volume, stock_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", \
                                                (date, info.code, info.name, info.open, info.high, info.low, info.close, info.volume, result[0]))
        else:
            db.cursor.execute("INSERT INTO daily(date, code, name, volume, stock_id) VALUES(?, ?, ?, ?, ?)", \
                                                (date, info.code, info.name, info.volume, stock_id))
        db.commit()
    else:
        logger.error(f"Cannot find stock for {info}")

def update_data_by_day():
    date = '20191105'

    url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?' + \
          'response=json&' + \
          'type=ALLBUT0999&' + \
          'date=' + str(date)
    data = get(url)
    if data is not None:
        data = json.loads(data)
        stat = data['stat']
        # 如果 stat 不是 OK，代表查詢日期尚無資料
        if stat != 'OK':
            logger.warning(f'There is no data at {date}')
            return

        #"fields9": ["證券代號", "證券名稱", "成交股數", "成交筆數", "成交金額", "開盤價", "最高價", "最低價", "收盤價", "漲跌(+/-)", "漲跌價差", "最後揭示買價", "最後揭示買量", "最後揭示賣價", "最後揭示賣量", "本益比"]
        #"data9": [["0050", "元大台灣50", "10,748,771", "4,277", "881,536,222", "81.45", "82.20", "81.40", "82.15", "+", "0.95", "82.15", "359", "82.20", "691", "0.00"],...
        # 所需資料表格位於第 9 表格
        records = data['data9']

        for record in records:
            try:
                code = record[0].strip()
                name = record[1].strip()
                volume = record[2].replace(',', '').strip()
                open = record[5].replace(',', '').strip()
                high = record[6].replace(',', '').strip()
                low = record[7].replace(',', '').strip()
                close = record[8].replace(',', '').strip()
                info = AfterHoursInfo(code, name, volume, open, high, low, close)
                add_daily(date, info)
            except:
                logger.error(traceback.format_exc())
    else:
        logger.error(f"Cannot get data from {url}")

#期交所資料 from 99年1月4日
def get_data_by_month(date, stock_number):
    #url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + date.strftime('%Y%m%d')+ "&stockNo=" + str(stock_number)
    data = json.loads(urlopen(url).read())

    '''
    {
        'stat': 'OK',
        'date': '20191104',
        'title': '108年11月2330台積電各日成交資訊',
        'fields': ['日期',
                   '成交股數',
                   '成交金額',
                   '開盤價',
                   '最高價',
                   '最低價',
                   '收盤價',
                   '漲跌價差',
                   '成交筆數'],
        'data': [['108/11/01',
                  '30,216,678',
                  '8,998,151,212',
                  '299.50',
                  '299.50',
                  '296.50',
                  '299.00',
                  '+0.50',
                  '10,
                   241']],
        'notes': ['符號說明: +/-/X表示漲/跌/不比價', '當日統計資訊含一般、零股、盤後定價、鉅額交易，不含拍賣、標購。', 'ETF證券代號第六碼為K、M、S、C者，表示該ETF以外幣交易。']
    }'''
    logger.info(data)
    #return pd.DataFrame(data['data'],columns=data['fields'])

CURRENT_YEAR = 2020
url = "https://goodinfo.tw/StockInfo/StockDividendPolicy.asp?STOCK_ID="
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}

def get_max_min_dy(stock_id):
    target_url = url + str(stock_id)

    try:
        res = get(target_url, headers)
        if res is not None:
            #with open("2884.txt", "w") as f:
            #    f.write(res)
        #with open("2883.txt", "r") as f:
        #    res = f.read()
        #if res:
            soup = BeautifulSoup(res, "lxml")
            #logger.info(soup.prettify())
            tbls = soup.find_all('table', {'class': 'solid_1_padding_4_0_tbl', 'width': '100%', 'bgcolor': '#d2d2d2'})
            for tbl in tbls:
                trs = tbl.find_all('tr')
                logger.info('%4s  %6s  %6s  %6s  %6s' % ("年度", "最高", "最低", "平均", "殖利率"))
                valid = CURRENT_YEAR
                for i in range(4, len(trs)):
                    #logger.info(trs[i])
                    tds = trs[i].find_all('td')
                    if len(tds) >= 19:
                        year = tds[12].get_text()
                        max = tds[13].get_text()
                        min = tds[14].get_text()
                        average = tds[15].get_text()
                        dy = tds[18].get_text()
                        if year.isdigit() and int(year) == valid:
                            logger.info('%6s  %8s  %8s  %8s  %8s' % (year, max, min, average, dy))
                            valid -= 1
    except:
        logger.error(traceback.format_exc())

def get_max_min_dy2(stock_id):
    target_url = url + str(stock_id)

    try:
        res = get(target_url, headers)
        if res is not None:
            soup = BeautifulSoup(res, "lxml")
            #logger.info(soup.prettify())
            tbls = soup.find_all('table', {'class': 'solid_1_padding_4_0_tbl', 'width': '100%', 'bgcolor': '#d2d2d2'})
            for tbl in tbls:
                trs = tbl.find_all('tr')
                logger.info('%4s  %6s  %6s  %6s  %6s' % ("年度", "最高", "最低", "平均", "殖利率"))

                if len(trs) < 9:
                    return

                valid = CURRENT_YEAR
                nums = list()
                #for i in range(4, len(trs)):
                for i in range(4, 10):
                    tds = trs[i].find_all('td')
                    if len(tds) >= 19:
                        year = tds[12].get_text()
                        max = tds[13].get_text()
                        min = tds[14].get_text()
                        average = tds[15].get_text()
                        dy = tds[18].get_text()
                        if year.isdigit() and int(year) == valid:
                            logger.info('%6s  %8s  %8s  %8s  %8s' % (year, max, min, average, dy))
                            valid -= 1
                            nums.append(float(min))
                import numpy as np
                print(np.std(np.array(nums), ddof=1))
    except:
        logger.error(traceback.format_exc())

def get_stocks():
    fs = open("stocks")
    line = fs.readline()
    while line:
        line = line.strip('\n')

        target_url = url + str(line)
        while True:
            time.sleep(5)
            try:
                res = get(target_url, headers)
                if res is not None:
                    logger.info(str(line))
                    path = os.path.join('data', str(line))
                    with open(path, "w") as f:
                        f.write(res)
                    break
            except:
                logger.error(traceback.format_exc())

        line = fs.readline()
    fs.close()
