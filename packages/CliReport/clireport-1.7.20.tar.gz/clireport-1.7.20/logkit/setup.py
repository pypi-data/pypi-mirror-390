# CliReport/logkit/setup.py
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
    تنظیم لاگ یکپارچه.
    متغیرهای محیطی اختیاری:
      LOG_LEVEL, LOG_FILE, LOG_JSON, LOG_MAX_BYTES, LOG_BACKUP_COUNT
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "")
    as_json = os.getenv("LOG_JSON", "0") == "1"
    max_bytes = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "3"))

    # ⛔️ مهم: دیگر از LogRecordFactory استفاده نکنید تا با extra تداخل نشود

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.filters.clear()

    formatter = JsonFormatter() if as_json else PlainFormatter()

    # کنسول
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    console.addFilter(TraceIdFilter())   # ← تضمین trace_id در لحظه‌ی emit
    root.addHandler(console)

    # فایل (اختیاری)
    if log_file:
        _ensure_dir(log_file)
        file_h = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_h.setFormatter(formatter)
        file_h.addFilter(TraceIdFilter())  # ← همین‌جا هم بگذار
        root.addHandler(file_h)

    # سطوح لاگ برای کتابخانه‌ها
    logging.getLogger("pyrogram").setLevel(level)
    logging.getLogger("pyrogram.session").setLevel(level)
    logging.getLogger("asyncio").setLevel("WARNING")

    # warnings → logging
    warnings.simplefilter("default")
    logging.captureWarnings(True)

    # استک‌دامپ روی کرش
    try:
        faulthandler.enable()
    except Exception:
        pass

    # این لاگ دیگر extra نمی‌فرستد؛ فیلتر روی هندلر خودش trace_id را اضافه می‌کند
    logging.getLogger("logkit.setup").info("Logging initialized")
