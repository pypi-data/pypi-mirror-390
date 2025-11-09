# CliReport/logging/formatters.py
import json
import logging

PLAIN_FMT = (
    "%(asctime)s %(levelname)s trace=%(trace_id)s "
    "%(name)s:%(lineno)d - %(message)s"
)

class PlainFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(PLAIN_FMT)

class JsonFormatter(logging.Formatter):
    """
    خروجی JSON برای ELK/Datadog/CloudWatch مناسب‌تر است.
    """
    default_time_format = "%Y-%m-%dT%H:%M:%S"

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": self.formatTime(record, self.default_time_format),
            "level": record.levelname,
            "logger": record.name,
            "line": record.lineno,
            "msg": record.getMessage(),
            "trace": getattr(record, "trace_id", "-"),
        }
        # پیام‌های اضافی استثناها اگر موجود بود
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)
