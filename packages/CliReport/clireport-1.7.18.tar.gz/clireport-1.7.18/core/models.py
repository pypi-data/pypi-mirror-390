# core/models.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, List

# لاگ‌گیری سرتاسری (trace-aware)
import logging
from logkit import get_trace_id, log_kv

logger = logging.getLogger(__name__)


class ReportReason(str, Enum):
    SPAM = "spam"
    VIOLENCE = "violence"
    PORNOGRAPHY = "pornography"
    CHILD_ABUSE = "child_abuse"
    ILLEGAL_DRUGS = "illegal_drugs"
    PERSONAL_DETAILS = "personal_details"
    COPYRIGHT = "copyright"
    GEO_IRRELEVANT = "geo_irrelevant"
    SCAM = "scam"
    FAKE = "fake"
    OTHER = "other"


@dataclass
class ReportRequest:
    target: str
    message_ids: Optional[List[int]] = None
    reason: ReportReason = ReportReason.SPAM
    comment: str = ""
    report_count: int = 1

    def __post_init__(self):
        trace = get_trace_id()

        # نرمال‌سازی report_count
        try:
            self.report_count = max(1, int(self.report_count))
        except Exception:
            self.report_count = 1

        # پاک‌سازی message_ids (اگر داده شده)
        if isinstance(self.message_ids, list):
            try:
                cleaned = [int(x) for x in self.message_ids if int(x) > 0]
            except Exception:
                cleaned = []
            self.message_ids = cleaned if cleaned else None

        # محدودسازی کامنت (اگر در Config محدودیت دارید می‌توانید همین‌جا اعمال کنید)
        # اینجا فقط trim سبک می‌کنیم
        self.comment = (self.comment or "").strip()

        # لاگ ساختاریافته
        preview = (self.comment[:50] + "…") if len(self.comment) > 50 else self.comment
        log_kv(
            logger, "ReportRequest.created",
            target=self.target,
            reason=getattr(self.reason, "value", self.reason),
            message_ids=self.message_ids,
            report_count=self.report_count,
            comment_preview=preview,
        )


@dataclass
class ReportResult:
    successful: int
    failed: int
    target: str
    reason: ReportReason
    comment: str
    message_ids: Optional[List[int]]
    start_time: datetime
    end_time: datetime
    # فیلد کمکی برای متادیتا (اختیاری)
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        trace = get_trace_id()

        # تضمین انواع/مقادیر معقول
        try:
            self.successful = int(self.successful)
        except Exception:
            self.successful = 0
        try:
            self.failed = int(self.failed)
        except Exception:
            self.failed = 0

        # پاک‌سازی idها (همان منطق Request)
        if isinstance(self.message_ids, list):
            try:
                cleaned = [int(x) for x in self.message_ids if int(x) > 0]
            except Exception:
                cleaned = []
            self.message_ids = cleaned if cleaned else None

        self.comment = (self.comment or "").strip()

        # لاگ ساختاریافته‌ی نتیجه
        log_kv(
            logger, "ReportResult.created",
            successful=self.successful,
            failed=self.failed,
            target=self.target,
            reason=getattr(self.reason, "value", self.reason),
            message_ids=self.message_ids,
            duration_sec=self.duration_seconds,
        )

    @property
    def duration_seconds(self) -> float:
        try:
            return max(0.0, (self.end_time - self.start_time).total_seconds())
        except Exception:
            return 0.0
