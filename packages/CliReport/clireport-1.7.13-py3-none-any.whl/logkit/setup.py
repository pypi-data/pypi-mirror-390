# CliReport/logging/setup.py
import logging
import os
import sys
import warnings
import faulthandler
from logging.handlers import RotatingFileHandler

from .filters import TraceIdFilter
from .formatters import PlainFormatter, JsonFormatter

def _ensure_dir(path: str):
    d = os.path.dirname(path)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def setup_logging():
    """
    راه‌اندازی لاگ یکپارچه برای کل برنامه.

    تنظیم از طریق متغیرهای محیطی:
      LOG_LEVEL = DEBUG | INFO | WARNING | ERROR   (پیش‌فرض: INFO)
      LOG_FILE  = مسیر فایل لاگ (خالی => فقط کنسول)
      LOG_JSON  = 1 برای خروجی JSON، غیر از آن => متن ساده
      LOG_MAX_BYTES = حداکثر حجم هر فایل (بایت) پیش‌فرض 5MB
      LOG_BACKUP_COUNT = تعداد نسخه‌های آرشیوی (پیش‌فرض 3)
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "")
    as_json = os.getenv("LOG_JSON", "0") == "1"
    max_bytes = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "3"))

    root = logging.getLogger()
    root.setLevel(level)
    # پاک کردن هندلرهای قبلی برای راه‌اندازی تمیز
    root.handlers.clear()
    root.filters.clear()

    # فیلتر trace_id
    trace_filter = TraceIdFilter()
    root.addFilter(trace_filter)

    # Formatter
    formatter = JsonFormatter() if as_json else PlainFormatter()

    # کنسول
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    # فایل (اختیاری)
    if log_file:
        _ensure_dir(log_file)
        file_h = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_h.setFormatter(formatter)
        root.addHandler(file_h)

    # سطح لاگ کتابخانه‌های اصلی
    logging.getLogger("pyrogram").setLevel(level)
    logging.getLogger("pyrogram.session").setLevel(level)
    # اگر نیاز به ریز شدن رخدادهای asyncio داشتید، این را DEBUG کنید
    logging.getLogger("asyncio").setLevel("WARNING")

    # warnings → logging
    warnings.simplefilter("default")
    logging.captureWarnings(True)

    # فعال‌سازی dump استک‌ها روی کرش/سیگنال
    try:
        faulthandler.enable()
    except Exception:
        pass

    logging.getLogger(__name__).info("Logging initialized", extra={"trace_id": "-"})
