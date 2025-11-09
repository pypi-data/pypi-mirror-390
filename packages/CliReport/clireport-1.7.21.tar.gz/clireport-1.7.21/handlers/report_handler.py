# handlers/report_handler.py
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from pyrogram import Client, filters
from pyrogram.types import Message

from core.models import ReportRequest, ReportResult
from core.validator import Validator
from core.config import Config
from core.executor import ReportExecutor
from utils.helpers import (
    smart_split,
    truncate_text,
    parse_entity_and_message_id,
    parse_message_ids,
)
from managers.response_builder import ResponseBuilder

# ---- لاگ‌گیری سرتاسری از پوشه‌ی CliReport/logging ---- 
from logkit import (
    setup_logging,   # فقط در entrypoint صدا زده می‌شود؛ اینجا نیاز نیست
    new_trace_id,
    with_trace,
    log_kv,
    get_trace_id,
)

logger = logging.getLogger(__name__)


def build_help() -> str:
    return (
        "دستور گزارش:\n"
        "`/report <entity> [message_id|id1,id2,...] <reason|alias> [comment...] [--count N]`\n\n"
        "نمونه‌ها:\n"
        "`/report @badchannel spam تبلیغات مکرر --count 3`\n"
        "`/report t.me/c/123/456 spam پیام اسپم`\n"
        "`/report @user 8,12 pornography`\n"
        "reason: spam | violence | pornography | child_abuse | illegal_drugs | personal_details | "
        "copyright | geo_irrelevant | scam | fake | other\n"
        "alias: مثل 'malware, phishing'، 'private images'، 'weapons' ..."
    )


def _debug_parts(parts: list[str]) -> str:
    """برای لاگ بهترِ آرگومان‌ها."""
    preview = []
    for i, p in enumerate(parts):
        if len(p) > 60:
            preview.append(f"[{i}]={p[:57]}…")
        else:
            preview.append(f"[{i}]={p}")
    return " ".join(preview)


def parse_args(text: str) -> Optional[ReportRequest]:
    """
    پارس دستور /report و تولید ReportRequest.
    در صورت نامعتبر بودن، None برمی‌گرداند.
    """
    trace = get_trace_id()
    logger.debug("parse_args: raw_text=%r", text, extra={"trace_id": trace})

    parts = smart_split(text)
    if not parts or not parts[0].startswith("/report"):
        logger.warning("parse_args: not a /report command", extra={"trace_id": trace})
        return None

    # حذف خود کلمه‌ی /report
    parts = parts[1:]
    if not parts:
        logger.warning("parse_args: missing args after /report", extra={"trace_id": trace})
        return None

    logger.debug("parse_args: parts=%s", _debug_parts(parts), extra={"trace_id": trace})

    # 1) entity و احتمالاً message_id از لینک
    entity_norm, msg_from_link = parse_entity_and_message_id(parts[0])
    message_ids = [msg_from_link] if isinstance(msg_from_link, int) else None
    logger.debug(
        "parse_args: entity_norm=%r msg_from_link=%r -> message_ids=%r",
        entity_norm, msg_from_link, message_ids, extra={"trace_id": trace}
    )

    # 2) اگر آرگومان دوم message_id یا لیست idها بود
    idx = 1
    if len(parts) > 1:
        cand = parts[1]
        if cand.isdigit() or ("," in cand and cand.replace(",", "").isdigit()):
            parsed = parse_message_ids(cand)
            if parsed:
                message_ids = parsed
                idx = 2
                logger.debug(
                    "parse_args: message_ids from arg2=%r", message_ids, extra={"trace_id": trace}
                )

    # 3) reason الزامی است
    if len(parts) <= idx:
        logger.warning("parse_args: missing reason", extra={"trace_id": trace})
        return None
    reason_str = parts[idx]
    idx += 1
    logger.debug("parse_args: reason_str=%r", reason_str, extra={"trace_id": trace})

    # 4) comment و --count اختیاری
    comment_parts: list[str] = []
    count = 1
    while idx < len(parts):
        if parts[idx] == "--count" and idx + 1 < len(parts) and parts[idx + 1].isdigit():
            count = int(parts[idx + 1])
            idx += 2
        else:
            comment_parts.append(parts[idx])
            idx += 1
    logger.debug(
        "parse_args: comment_parts=%r count=%r", comment_parts, count, extra={"trace_id": trace}
    )

    # 5) reason را ولیدیت/نرمال کنید
    ok, reason, alias_note = Validator.parse_reason(reason_str)
    log_kv(
        logger, "parse_args: reason parsed",
        ok=ok,
        input=reason_str,
        reason=getattr(reason, "value", None),
        alias_note=alias_note,
    )
    # 6) اعتبارسنجی entity/message_ids
    if not ok or not Validator.validate_entity(entity_norm) or not Validator.validate_message_ids(message_ids):
        logger.warning(
            "parse_args: validation failed ok=%r entity_ok=%r ids_ok=%r",
            ok,
            Validator.validate_entity(entity_norm),
            Validator.validate_message_ids(message_ids),
            extra={"trace_id": trace},
        )
        return None

    # 7) نهایی‌سازی comment
    comment = " ".join(comment_parts).strip()
    if alias_note and alias_note.lower() not in (comment or "").lower():
        comment = f"{alias_note}. {comment}".strip()
    comment = truncate_text(comment, Config.MAX_COMMENT_LENGTH)

    req = ReportRequest(
        target=entity_norm,
        message_ids=message_ids,
        reason=reason,
        comment=comment or "",
        report_count=count,
    )
    log_kv(
        logger, "parse_args: OK",
        target=req.target,
        reason=getattr(req.reason, "value", None),
        message_ids=req.message_ids,
        count=req.report_count,
        comment_preview=(req.comment[:50] + "…") if len(req.comment) > 50 else req.comment,
    )
    return req


def register_handlers(app: Client) -> None:
    @app.on_message(filters.command("start"))
    @with_trace(__name__)
    async def start_handler(client: Client, message: Message):
        # هر دستور، trace جدید
        new_trace_id()
        log_kv(
            logger, "command /start received",
            chat_id=getattr(message.chat, "id", None),
            user_id=getattr(message.from_user, "id", None),
            text=message.text,
        )
        await message.reply_text("سلام! برای گزارش از دستور زیر استفاده کن:\n\n" + build_help())

    @app.on_message(filters.command("help"))
    @with_trace(__name__)
    async def help_handler(client: Client, message: Message):
        new_trace_id()
        log_kv(
            logger, "command /help received",
            chat_id=getattr(message.chat, "id", None),
            user_id=getattr(message.from_user, "id", None),
        )
        await message.reply_text(build_help())

    @app.on_message(filters.command("report"))
    @with_trace(__name__)
    async def report_handler(client: Client, message: Message):
        new_trace_id()
        trace = get_trace_id()
        log_kv(
            logger, "command /report received",
            chat_id=getattr(message.chat, "id", None),
            user_id=getattr(message.from_user, "id", None),
            text=message.text,
        )

        req = parse_args(message.text or "")
        if req is None:
            logger.warning("report_handler: parse_args returned None", extra={"trace_id": trace})
            await message.reply_text("❗ ورودی نامعتبر.\n\n" + build_help())
            return

        processing = await message.reply_text("⏳ در حال ارسال گزارش…")
        executor = ReportExecutor(client)

        start = datetime.now()
        ok, fail = False, 0
        try:
            logger.debug(
                "report_handler: executor.run start target=%r reason=%r ids=%r comment_len=%d count=%d",
                req.target,
                getattr(req.reason, "value", req.reason),
                req.message_ids,
                len(req.comment or ""),
                req.report_count,
                extra={"trace_id": trace},
            )
            ok, fail = await executor.run(req)
            logger.debug(
                "report_handler: executor.run done ok=%r fail=%r",
                ok, fail, extra={"trace_id": trace}
            )
        except Exception as e:
            logger.exception("report_handler: executor.run failed: %s", e, extra={"trace_id": trace})
            await processing.edit_text(f"❌ اجرای گزارش دچار خطا شد:\n\n`{e}`")
            return

        end = datetime.now()

        result = ReportResult(
            successful=ok,
            failed=fail,
            target=req.target,
            reason=req.reason,
            comment=req.comment or "",
            message_ids=req.message_ids,
            start_time=start,
            end_time=end,
        )

        summary = ResponseBuilder.build_summary_text(result)
        await processing.edit_text(summary)

        # لاگ ساختاریافته از خلاصه
        log_kv(
            logger, "report summary",
            successful=ok,
            failed=fail,
            target=req.target,
            reason=getattr(req.reason, "value", req.reason),
            message_ids=req.message_ids,
            duration_sec=(end - start).total_seconds(),
        )
