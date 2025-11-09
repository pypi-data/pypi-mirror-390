
import logging
from logging.handlers import RotatingFileHandler
from core.config import Config

def setup_logging() -> None:
    logger = logging.getLogger()
    logger.setLevel(Config.LOG_LEVEL)
    fmt = logging.Formatter(Config.LOG_FORMAT)

    ch = logging.StreamHandler()
    ch.setFormatter(fmt)
    ch.setLevel(Config.LOG_LEVEL)
    logger.addHandler(ch)

    fh = RotatingFileHandler('report_bot.log', maxBytes=2_000_000, backupCount=3, encoding='utf-8')
    fh.setFormatter(fmt)
    fh.setLevel(Config.LOG_LEVEL)
    logger.addHandler(fh)
