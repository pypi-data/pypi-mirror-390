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
      LOG_LEVEL, LOG_FILE, LOG_JSON, LOG_MAX_BYTES, LOG_BACKUP_COUNT
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = os.getenv("LOG_FILE", "")
    as_json = os.getenv("LOG_JSON", "0") == "1"
    max_bytes = int(os.getenv("LOG_MAX_BYTES", str(5 * 1024 * 1024)))
    backup_count = int(os.getenv("LOG_BACKUP_COUNT", "3"))

    # --- 1) LogRecordFactory: تزریق trace_id برای همه رکوردها (حتی لاگ‌های کتابخانه‌ها) ---
    orig_factory = logging.getLogRecordFactory()
    def record_factory(*args, **kwargs):
        record = orig_factory(*args, **kwargs)
        if not hasattr(record, "trace_id"):
            record.trace_id = "-"   # مقدار پیش‌فرض
        return record
    logging.setLogRecordFactory(record_factory)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.filters.clear()

    # Formatter
    formatter = JsonFormatter() if as_json else PlainFormatter()

    # --- 2) هندلر کنسول ---
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    # فیلتر روی هندلر (تا مطمئن شویم trace_id همیشه هست)
    console.addFilter(TraceIdFilter())
    root.addHandler(console)

    # --- 3) هندلر فایل (اختیاری) ---
    if log_file:
        _ensure_dir(log_file)
        file_h = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_h.setFormatter(formatter)
        file_h.addFilter(TraceIdFilter())
        root.addHandler(file_h)

    # سطح لاگ کتابخانه‌ها
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

    logging.getLogger("logkit.setup").info("Logging initialized", extra={"trace_id": "-"})
