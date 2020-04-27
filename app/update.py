import datetime
import json
from app.foundation import logger
import app.constants as CONST

class UpdateInfo(object):
    def __init__(self):
        with open(CONST.UPDATE_FILE, "r") as f:
            self.data = json.load(f)

    def update(self):
        with open(CONST.UPDATE_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def update_stock_date(self):
        today = datetime.date.today().strftime('%Y%m%d')
        self.data['stock'] = today
        self.update()

    def update_daily(self):
        today = datetime.date.today().strftime('%Y%m%d')
        self.data['stock'] = today
        self.update()
