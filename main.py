import traceback

import datetime
from app.foundation import logger
from app.stocks import update_stocks, update_data_by_day, get_max_min_dy, get_stocks
from globals import db

if __name__ == '__main__':
    while True:
        try:
            print("1) 查詢歷年股價及殖利率")
            print("2) 更新股票清單")
            print("3) 取得歷年股價")
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
                get_stocks()
            elif op == 'Q' or op == 'q':
                break
            else:
                print("輸入錯誤")
        #update_data_by_day()
        except:
            logger.error(traceback.format_exc())
    db.close()