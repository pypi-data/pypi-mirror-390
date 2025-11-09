# CliReport/logkit/__init__.py
from .setup import setup_logging
from .trace import new_trace_id, get_trace_id, with_trace, log_kv

__all__ = [
    "setup_logging",
    "new_trace_id",
    "get_trace_id",
    "with_trace",
    "log_kv",
]
