# CliReport/logging/filters.py
import logging

class TraceIdFilter(logging.Filter):
    """
    اگر رکورد لاگ trace_id نداشت، مقدار پیش‌فرض '-'
    به آن اضافه می‌کند تا Formatter ها بدون خطا کار کنند.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "trace_id"):
            record.trace_id = "-"
        return True
