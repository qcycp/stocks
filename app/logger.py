import datetime
import os
from loguru import logger
from config import LOGDIR

class Logger(object):
    def __init__(self):
        logger.add(
            os.path.join(LOGDIR, f'{datetime.date.today():%Y%m%d}.log'),
            rotation='50 MB',
            retention='180 days',
            level='DEBUG'
        )
        self.__logger = logger

    def get_logger(self):
        return self.__logger