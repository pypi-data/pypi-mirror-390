# CliReport/logging/trace.py
import time
import uuid
import logging
from contextvars import ContextVar
from functools import wraps

_current_trace: ContextVar[str] = ContextVar("trace_id", default="-")

def new_trace_id() -> str:
    """
    برای هر درخواست/دستور جدید صدا بزنید تا trace_id یکتا ساخته شود.
    """
    t = uuid.uuid4().hex[:12]
    _current_trace.set(t)
    return t

def get_trace_id() -> str:
    return _current_trace.get()

def with_trace(logger_name: str | None = None):
    """
    دکوریتور async برای لاگ ورود/خروج و زمان اجرا با trace_id جاری.
    """
    def deco(fn):
        log = logging.getLogger(logger_name or fn.__module__)

        @wraps(fn)
        async def wrapper(*args, **kwargs):
            trace = get_trace_id()
            start = time.perf_counter()
            log.debug(f"→ {fn.__name__} enter", extra={"trace_id": trace})
            try:
                res = await fn(*args, **kwargs)
                dur_ms = (time.perf_counter() - start) * 1000
                log.debug(f"← {fn.__name__} ok ({dur_ms:.1f} ms)", extra={"trace_id": trace})
                return res
            except Exception as e:
                dur_ms = (time.perf_counter() - start) * 1000
                log.exception(f"× {fn.__name__} failed ({dur_ms:.1f} ms): {e}", extra={"trace_id": trace})
                raise
        return wrapper
    return deco

def log_kv(logger: logging.Logger, msg: str, **kv):
    """
    برای لاگ‌های ساختاریافتهٔ ساده (کلید/مقدار) با trace_id جاری.
    """
    trace = get_trace_id()
    # فیلتر کردن None ها
    kv = {k: v for k, v in kv.items() if v is not None}
    line = msg
    if kv:
        line += " " + " ".join(f"{k}={v!r}" for k, v in kv.items())
    logger.info(line, extra={"trace_id": trace})
