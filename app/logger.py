import datetime
from loguru import logger

class Logger(object):
    def __init__(self):
        logger.add(
            f'{datetime.date.today():%Y%m%d}.log',
            rotation='50 MB',
            retention='180 days',
            level='DEBUG'
        )
        self.__logger = logger

    def get_logger(self):
        return self.__logger