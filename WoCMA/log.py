import logging
from logging.handlers import RotatingFileHandler


class SingletonLogger:
    _logger = None

    @staticmethod
    def get_logger():
        if SingletonLogger._logger is None:
            SingletonLogger._logger = logging.getLogger("AppName")

            handler = RotatingFileHandler('debug.log', maxBytes=5 * 1024 * 1024, backupCount=3)

            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - Line: %(lineno)d')
            handler.setFormatter(formatter)
            SingletonLogger._logger.addHandler(handler)
            SingletonLogger._logger.setLevel(logging.INFO)
        return SingletonLogger._logger
