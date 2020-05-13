import os
import traceback

import datetime
from config import DATADIR, LOGDIR, RAWDIR
from app.foundation import logger
from app.stocks import update_stocks
from app.stocks import update_data_by_day
from app.stocks import get_max_min_dy
from app.stocks import update_stocks_raw_data_from_goodinfo
from app.stocks import get_effective_tracking_list
from globals import db

if __name__ == '__main__':
    if not os.path.exists(DATADIR):
        os.makedirs(DATADIR, exist_ok=True)
    if not os.path.exists(LOGDIR):
        os.makedirs(LOGDIR, exist_ok=True)
    if not os.path.exists(RAWDIR):
        os.makedirs(RAWDIR, exist_ok=True)

    while True:
        try:
            print("1) 查詢歷年股價及殖利率")
            print("2) 更新股票清單 from TWSE")
            print("3) 更新歷年股價資料 from Goodinfo")
            print("4) 篩選波動穩動的最低股價清單")
            print("q) 離開")
            op = input('請選取操作: ')
            if op == '1':
                while True:
                    sid = input('請輸入股票ID (q回主選單): ')
                    if sid == 'q':
                        break
                    get_max_min_dy(sid)
            elif op == '2':
                update_stocks()
            elif op == '3':
                update_stocks_raw_data_from_goodinfo()
            elif op == '4':
                get_effective_tracking_list()
            elif op == 'Q' or op == 'q':
                break
            else:
                print("輸入錯誤")
        #update_data_by_day()
        except:
            logger.error(traceback.format_exc())
    db.close()