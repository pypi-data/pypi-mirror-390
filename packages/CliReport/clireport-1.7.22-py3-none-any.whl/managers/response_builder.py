# managers/response_builder.py
from __future__ import annotations

import logging
from typing import List, Dict, Any

from core.models import ReportResult
from logkit.trace import get_trace_id

logger = logging.getLogger(__name__)


def _fmt_ids(ids: List[int] | None) -> str:
    return ", ".join(map(str, ids)) if ids else "-"


def _percent(success: int, fail: int) -> float:
    total = success + fail
    return (success / total) * 100.0 if total > 0 else 0.0


def _build_flow_summary(meta: Dict[str, Any]) -> str:
    """
    خلاصه‌ای کوتاه و خوانا از مسیر منوهای تلگرام.
    """
    flow = meta.get("flow") or []
    if not flow:
        return ""

    lines: List[str] = []
    for step in flow[:6]:  # خلاصه نگه داریم
        t = step.get("type")
        if t == "choose":
            title = step.get("title") or "Choose"
            opts = step.get("options") or []
            # فقط تیتر، نه تمام گزینه‌ها (خیلی طولانی می‌شود)
            lines.append(f"↳ {title}")
        elif t == "pick":
            lines.append("✓ گزینه انتخاب شد")
        elif t == "add_comment":
            lines.append("✎ نیاز به توضیح")
        else:
            lines.append(f"… {t}")
    return "\n".join(lines)


class ResponseBuilder:
    @staticmethod
    def build_summary_text(result: ReportResult) -> str:
        """
        رشته‌ی خلاصه‌ی نهایی برای نمایش در تلگرام.
        علاوه بر آمار، وضعیت «ثبت در تلگرام» (بر اساس ReportResultReported) را هم نشان می‌دهد.
        """
        trace = get_trace_id()
        success = int(result.successful)
        fail = int(result.failed)
        eff = _percent(success, fail)

        # اطلاعات متای اجرا (از Executor)
        meta = getattr(result, "meta", {}) or {}
        reported = bool(meta.get("reported"))
        peer_report = bool(meta.get("peer_report"))
        result_type = meta.get("result_type") or "-"

        status_line = "🟢 ثبت در تلگرام: تایید شد" if reported else "🟡 ثبت در تلگرام: نامشخص"
        # برای گزارش روی peer، نوع نتیجه معمولاً بولی است
        if peer_report and reported:
            status_line = "🟢 گزارش کاربر/کانال ثبت شد"

        flow_summary = _build_flow_summary(meta)

        text = (
            "📊 گزارش عملیات گزارش‌دهی\n\n"
            f"✅ موفق: {success}\n"
            f"❌ ناموفق: {fail}\n"
            f"⏱️ زمان اجرا: {result.end_time - result.start_time}\n"
            f"📈 کارایی: {eff:.1f}%\n"
            f"🎯 هدف: {result.target}\n"
            f"#️⃣ آی‌دی پیام(ها): {_fmt_ids(result.message_ids)}\n"
            f"🧩 دلیل: {getattr(result.reason, 'value', result.reason)}\n"
            f"📝 توضیح: {result.comment or '-'}\n"
            f"{status_line}\n"
        )

        # اگر خلاصه‌ی مسیر داریم، اضافه کنیم
        if flow_summary:
            text += flow_summary + "\n"

        # یک خط دیباگ سبک (نوع نتیجه‌ی آخر تلگرام)
        text += f"ℹ️ نتیجه تلگرام: {result_type}"

        logger.debug("response built", extra={"trace_id": trace})
        return text
