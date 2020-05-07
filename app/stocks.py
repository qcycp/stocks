import datetime
import json
import os
import requests
import time
import traceback
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from urllib.request import urlopen

import app.constants as CONST
from app.after_hours import AfterHoursInfo
from app.api_utils import get
from app.constants import LISTED_TYPE, GOODINFO_URL
from app.foundation import logger
from config import RAWDIR
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

def get_max_min_dy(stock_id, online=False):
    try:
        res = None
        if online:
            target_url = GOODINFO_URL + str(stock_id)
            res = get(target_url)
        else:
            target = os.path.join(RAWDIR, str(stock_id))
            if os.path.exists(target):
                with open(target, 'r') as f:
                    res = f.read()

        if res is not None:
            if online:
                path = os.path.join(RAWDIR, str(stock_id))
                with open(path, "w") as f:
                    f.write(res)
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

def get_effective_tracking_list(now=True):
    TRACKING_YEARS = 5
    VOLUME_THRESHOLD = 250
    STD_THRESHOLD = 2
    PROFIT_THRESHOLD = 0.3
    READY_TO_BUY_THRESHOLD = 0.05
    try:
        fs = open(CONST.STOCKS_FILE)
        line = fs.readline()
        while line:
            line = line.strip('\n')
            target = os.path.join(RAWDIR, str(line))

            if os.path.exists(target):
                with open(target, 'r') as f:
                    res = f.read()

            if res is not None and '瀏覽量異常' not in res:
                volume = get_volume(res)
                close = 0
                if now:
                    close = get_close(res)
                # condition 1: 成交量 > 250
                if volume > VOLUME_THRESHOLD:
                    soup = BeautifulSoup(res, "lxml")
                    tbls = soup.find_all('table', {'class': 'solid_1_padding_4_0_tbl', 'width': '100%', 'bgcolor': '#d2d2d2'})
                    for tbl in tbls:
                        trs = tbl.find_all('tr')

                        valid = CURRENT_YEAR
                        max_list = list()
                        min_list = list()
                        for i in range(4, len(trs)):
                            tds = trs[i].find_all('td')
                            if len(tds) >= 19:
                                year = tds[12].get_text()
                                max = tds[13].get_text()
                                min = tds[14].get_text()
                                if year.isdigit() and int(year) == valid:
                                    valid -= 1
                                    max_list.append(float(max))
                                    min_list.append(float(min))
                                    if len(max_list) == TRACKING_YEARS:
                                        break
                                else:
                                    break

                    # condition 2: 歷史紀錄超過5年
                    if len(max_list) == TRACKING_YEARS:
                        #logger.info('STD of last %s year: %s' % (len(min_list), np.std(np.array(min_list), ddof=1)))
                        std = np.std(np.array(min_list), ddof=1)
                        # condition 3: 最低股價樣本標準差 < 2
                        if std < STD_THRESHOLD:
                            avg_max = sum(max_list) / len(max_list)
                            avg_min = sum(min_list) / len(min_list)
                            # condition 4: 平均最高股價比平均最低股價 > 30%
                            if (avg_max - avg_min)/avg_max > PROFIT_THRESHOLD:
                                if now:
                                    # 挑選當前股價適合進場的標的: 當前股價大於平均最低股價不超過5%
                                    if (close - avg_min)/avg_min < READY_TO_BUY_THRESHOLD:
                                        logger.info('%s' % line)
                                else:
                                    logger.info('%s : %s' % (line, std))

            line = fs.readline()
    except:
        logger.error(traceback.format_exc())

def calculate_std(stock_id, _range=5, online=False):
    try:
        res = None
        if online:
            target_url = GOODINFO_URL + str(stock_id)
            res = get(target_url)
        else:
            target = os.path.join(RAWDIR, str(stock_id))
            if os.path.exists(target):
                with open(target, 'r') as f:
                    res = f.read()

        if res is not None and '瀏覽量異常' not in res:
            soup = BeautifulSoup(res, "lxml")
            #logger.info(soup.prettify())
            tbls = soup.find_all('table', {'class': 'solid_1_padding_4_0_tbl', 'width': '100%', 'bgcolor': '#d2d2d2'})
            for tbl in tbls:
                trs = tbl.find_all('tr')

                valid = CURRENT_YEAR
                nums = list()
                for i in range(4, len(trs)):
                    tds = trs[i].find_all('td')
                    if len(tds) >= 19:
                        year = tds[12].get_text()
                        max = tds[13].get_text()
                        min = tds[14].get_text()
                        average = tds[15].get_text()
                        dy = tds[18].get_text()
                        if year.isdigit() and int(year) == valid:
                            valid -= 1
                            nums.append(float(min))

                            if len(nums) == _range:
                                break
                        else:
                            break

                logger.info('STD of last %s year: %s' % (len(nums), np.std(np.array(nums), ddof=1)))
    except:
        logger.error(traceback.format_exc())

def update_stocks_raw_data():
    today = datetime.date.today()
    today = today.strftime('%m/%d')
    logger.info('today : %s' % today)

    try:
        fs = open(CONST.STOCKS_FILE)
        line = fs.readline()
        while line:
            line = line.strip('\n')
            target = os.path.join(RAWDIR, str(line))

            to_be_update = False
            if os.path.exists(target):
                with open(target, 'r') as f:
                    res = f.read()

                if res is not None:
                    soup = BeautifulSoup(res, "lxml")
                    date = soup.find('nobr', {'style': 'font-size:9pt;color:gray;'})
                    if not date:
                        to_be_update = True
                    else:
                        date = date.get_text().split()[1]
                        if date != today:
                            to_be_update = True
                else:
                    to_be_update = True
            else:
                to_be_update = True

            if to_be_update:
                logger.info('%s updating...' % str(line))
                target_url = GOODINFO_URL + str(line)

                while True:
                    #time.sleep(5)
                    try:
                        res = get(target_url)
                        if res is not None and '瀏覽量異常' not in res:
                            path = os.path.join(RAWDIR, str(line))
                            with open(path, "w") as f:
                                f.write(res)
                            break
                    except:
                        logger.error(traceback.format_exc())
            else:
                logger.info('%s is ready' % str(line))
            line = fs.readline()
    except:
        logger.error(traceback.format_exc())

def get_volume(text):
    volume = 0
    soup = BeautifulSoup(text, "lxml")
    tbl = soup.find('table', {'class': 'solid_1_padding_3_2_tbl', 'border': '0', 'cellspacing': '0', 'cellpadding': '0', 'style': 'width:100%;font-size:11pt;'})
    if tbl:
        trs = tbl.find_all('tr')
        tds = trs[5].find_all('td')
        volume = tds[0].get_text().replace(',', '')
    return int(volume)

def get_close(text):
    close = 0
    soup = BeautifulSoup(text, "lxml")
    tbl = soup.find('table', {'class': 'solid_1_padding_3_2_tbl', 'border': '0', 'cellspacing': '0', 'cellpadding': '0', 'style': 'width:100%;font-size:11pt;'})
    if tbl:
        trs = tbl.find_all('tr')
        tds = trs[3].find_all('td')
        close = tds[0].get_text()
    return float(close)