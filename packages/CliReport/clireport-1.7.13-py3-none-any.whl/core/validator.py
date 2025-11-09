# core/validator.py
from __future__ import annotations

import logging
from typing import Optional, List, Tuple

from core.models import ReportReason
from utils.helpers import validate_t_me_link
from data.constants import ALIAS_TO_REASON

# لاگ‌گیری سرتاسری
from CliReport.logkit import get_trace_id, log_kv

logger = logging.getLogger(__name__)


class Validator:
    @staticmethod
    def validate_entity(entity: str) -> bool:
        """
        اعتبارسنجی entity (یوزرنیم/لینک t.me/…)
        """
        trace = get_trace_id()
        ok = False
        try:
            ok = bool(validate_t_me_link(entity))
            log_kv(
                logger, "validator.validate_entity",
                entity=entity,
                ok=ok
            )
            return ok
        except Exception as e:
            logger.exception("validate_entity failed: %s", e, extra={"trace_id": trace})
            return False

    @staticmethod
    def validate_message_ids(message_ids: Optional[List[int]]) -> bool:
        """
        اعتبارسنجی لیست message_id ها (باید > 0 باشند). None مجاز است.
        """
        trace = get_trace_id()
        if message_ids is None:
            log_kv(logger, "validator.validate_message_ids", ids="None", ok=True)
            return True
        try:
            ok = all(int(x) > 0 for x in message_ids)
            log_kv(logger, "validator.validate_message_ids", ids=message_ids, ok=ok)
            return ok
        except Exception as e:
            logger.exception("validate_message_ids failed: %s", e, extra={"trace_id": trace})
            return False

    @staticmethod
    def parse_reason(reason_str: str) -> Tuple[bool, Optional[ReportReason], Optional[str]]:
        """
        پارس و نرمال‌سازی دلیل گزارش.
        خروجی: (ok, reason enum یا None, alias_note یا None)
        """
        trace = get_trace_id()
        if not reason_str:
            log_kv(logger, "validator.parse_reason", input=None, ok=False)
            return False, None, None

        norm = reason_str.strip().lower()
        logger.debug("parse_reason: norm=%r", norm, extra={"trace_id": trace})

        # 1) تلاش مستقیم با Enum
        try:
            reason = ReportReason(norm)
            log_kv(
                logger, "validator.parse_reason.enum",
                input=norm, ok=True, reason=reason.value
            )
            return True, reason, None
        except Exception:
            logger.debug("parse_reason: not direct enum", extra={"trace_id": trace})

        # 2) تلاش با Alias
        alias = ALIAS_TO_REASON.get(norm)
        if alias:
            mapped, note = alias
            try:
                reason = ReportReason(mapped)
                log_kv(
                    logger, "validator.parse_reason.alias",
                    input=norm, mapped=mapped, ok=True, note=note
                )
                return True, reason, (note or None)
            except Exception:
                # اگر مقدار مپ‌شده Enum نبود، به OTHER بیفتد اما note حفظ شود
                log_kv(
                    logger, "validator.parse_reason.alias.fallback_other",
                    input=norm, mapped=mapped, ok=True, note=note
                )
                return True, ReportReason.OTHER, (note or None)

        # 3) نامعتبر
        log_kv(logger, "validator.parse_reason.invalid", input=norm, ok=False)
        return False, None, None
