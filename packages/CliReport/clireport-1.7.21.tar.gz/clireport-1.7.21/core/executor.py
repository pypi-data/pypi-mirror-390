# core/executor.py
from __future__ import annotations

import asyncio
import logging
from time import perf_counter
from typing import Tuple, Dict, Any, Iterable, Optional

from pyrogram import Client
from pyrogram.errors import (
    FloodWait, PeerIdInvalid, ChannelInvalid, UserNotParticipant, ChatAdminRequired, RPCError
)
from pyrogram.raw import functions, types

from core.models import ReportRequest
from data.constants import REASON_MAPPING
from core.config import Config

from logkit import get_trace_id, with_trace, log_kv

logger = logging.getLogger(__name__)


def _normalize(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _pick_option_by_reason(reason_value: str, options: Iterable[types.MessageReportOption]) -> Optional[bytes]:
    """
    انتخاب «بهترین» گزینه از میان options با توجه به reason.
    هم کلیدواژه‌های انگلیسی را چک می‌کند هم فارسی.
    """
    r = _normalize(reason_value)

    # کلیدواژه‌ها (EN + FA)
    kw = {
        "spam": ["spam", "advert", "ads", "promo", "تبلیغ", "اسپم"],
        "violence": ["violence", "harm", "threat", "خشونت", "تهدید", "آزار"],
        "pornography": ["porn", "sexual", "adult", "sex", "هرزه", "پورن", "پورنو", "پورنوگرافی", "محتوای جنسی", "جنسی"],
        "child_abuse": ["child", "minor", "کودک", "نابالغ", "آزار کودک"],
        "illegal_drugs": ["drug", "narcotic", "مواد", "مخدر", "مواد مخدر"],
        "personal_details": ["personal", "private", "dox", "اطلاعات شخصی", "حریم خصوصی", "شماره"],
        "copyright": ["copyright", "dmca", "حق نشر", "کپی‌رایت"],
        "geo_irrelevant": ["geo", "location", "irrelevant", "بی‌ربط", "نامرتبط", "جغرافیایی"],
        "scam": ["scam", "fraud", "phish", "کلاهبرداری", "فیشینگ", "تقلب"],
        "fake": ["fake", "impersonat", "misleading", "جعلی", "جعل", "هویت جعلی", "گمراه‌کننده"],
        "other": ["other", "misc", "سایر", "دیگر"],
    }
    keys = kw.get(r, []) + [r]

    # تلاش برای مچ با متن گزینه‌ها
    best = None
    for opt in options or []:
        text = _normalize(getattr(opt, "text", ""))
        if any(k in text for k in keys):
            return getattr(opt, "option", None)
        if best is None:
            best = getattr(opt, "option", None)
    return best  # fallback: اولی


async def _safe_invoke(client: Client, func_cls, **kwargs) -> Any:
    trace = get_trace_id()
    name = getattr(func_cls, "__name__", str(func_cls))
    start = perf_counter()
    try:
        logger.debug("invoke.call func=%s kwargs=%r", name, list(kwargs.keys()), extra={"trace_id": trace})
        res = await client.invoke(func_cls(**kwargs))
        dur = (perf_counter() - start) * 1000
        logger.info("invoke.ok func=%s (%.1f ms)", name, dur, extra={"trace_id": trace})
        return res
    except Exception:
        dur = (perf_counter() - start) * 1000
        logger.exception("invoke.failed func=%s (%.1f ms)", name, dur, extra={"trace_id": trace})
        raise


class ReportExecutor:
    def __init__(self, client: Client):
        self.client = client

    @with_trace(__name__)
    async def _report_message(self, req: ReportRequest) -> bool:
        """
        جریان چندمرحله‌ای messages.Report (Layer 214):
          - Stage1: option=b""
          - ممکن است ChooseOption بیاید (یک یا چند سطح)
          - ممکن است AddComment بیاید
          - در نهایت Reported
        """
        trace = get_trace_id()
        peer = await self.client.resolve_peer(req.target)
        ids = req.message_ids or []
        comment = req.comment or ""
        reason_val = getattr(req.reason, "value", str(req.reason)).lower()

        # چاپ ورودی‌ها
        logger.debug(
            "report_message.start target=%r ids=%r reason=%r comment_len=%d",
            req.target, ids, reason_val, len(comment),
            extra={"trace_id": trace},
        )

        # حلقهٔ مقاوم با حداکثر عمق (برای منوهای چندسطحی)
        max_steps = 5
        visited_options: set[bytes] = set()
        current_option: bytes = b""

        for step in range(1, max_steps + 1):
            logger.debug(
                "messages.Report step=%d option=%r comment_len=%d",
                step, current_option, len(comment),
                extra={"trace_id": trace},
            )

            try:
                res = await _safe_invoke(
                    self.client,
                    functions.messages.Report,
                    peer=peer,
                    id=ids,
                    option=current_option,
                    message=comment,
                )
            except FloodWait as e:
                logger.warning("FloodWait %ss", e.value, extra={"trace_id": trace})
                await asyncio.sleep(int(e.value))
                return False
            except (PeerIdInvalid, ChannelInvalid, UserNotParticipant, ChatAdminRequired) as e:
                logger.error("messages.Report failed: %s", type(e).__name__, extra={"trace_id": trace})
                return False
            except RPCError as e:
                logger.error("messages.Report RPCError: %s", e, extra={"trace_id": trace})
                return False
            except Exception:
                logger.error("messages.Report unexpected", exc_info=True, extra={"trace_id": trace})
                return False

            # تفسیر نتایج
            if isinstance(res, types.ReportResultReported):
                log_kv(logger, "messages.Report.reported", target=req.target, ids=ids, step=step)
                return True

            if isinstance(res, types.ReportResultAddComment):
                # اینجا option قطعی شده؛ حالا باید با کامنت ارسال کنیم
                final_comment = comment or reason_val
                logger.debug(
                    "messages.Report AddComment → option=%r final_comment_len=%d",
                    res.option, len(final_comment),
                    extra={"trace_id": trace},
                )
                try:
                    res2 = await _safe_invoke(
                        self.client,
                        functions.messages.Report,
                        peer=peer,
                        id=ids,
                        option=res.option,
                        message=final_comment,
                    )
                except Exception:
                    logger.error("AddComment follow-up failed", exc_info=True, extra={"trace_id": trace})
                    return False
                ok = isinstance(res2, types.ReportResultReported)
                log_kv(logger, "messages.Report.final", ok=ok)
                return bool(ok)

            if isinstance(res, types.ReportResultChooseOption):
                # لاگ کامل منو برای دیباگ
                opts_preview = [f"{i+1}. {getattr(o, 'text', '')}" for i, o in enumerate(res.options or [])]
                log_kv(logger, "ChooseOption", title=getattr(res, "title", ""), options=" | ".join(opts_preview))

                # بر اساس reason بهترین گزینه را انتخاب کن
                picked = _pick_option_by_reason(reason_val, res.options)
                if not picked:
                    logger.error("no matching option for reason=%r", reason_val, extra={"trace_id": trace})
                    return False

                # جلوگیری از حلقه: اگر قبلاً همین option را زده‌ایم، بی‌خیال
                if picked in visited_options:
                    logger.error("loop detected on option=%r", picked, extra={"trace_id": trace})
                    return False
                visited_options.add(picked)

                # به مرحله بعد با option انتخابی
                current_option = picked
                # نکته: بعضی زیرمنوها نیاز به comment دارند؛ ما comment فعلی را همان‌طور می‌فرستیم
                # (در صورت نیاز AddComment برمی‌گردد و مرحله بعد پوششش می‌دهد)
                continue

            # نتیجهٔ غیرمنتظره
            logger.error("unexpected ReportResult type: %r", type(res).__name__, extra={"trace_id": trace})
            return False

        # از حد مراحل گذشتیم
        logger.error("report_message exceeded max steps=%d", max_steps, extra={"trace_id": trace})
        return False

    @with_trace(__name__)
    async def _report_peer(self, req: ReportRequest) -> bool:
        trace = get_trace_id()
        peer = await self.client.resolve_peer(req.target)
        reason_obj = REASON_MAPPING[req.reason]
        logger.debug(
            "account.ReportPeer → target=%r reason=%s comment_len=%d",
            req.target, type(reason_obj).__name__, len(req.comment or ""),
            extra={"trace_id": trace},
        )
        try:
            res = await _safe_invoke(
                self.client,
                functions.account.ReportPeer,
                peer=peer,
                reason=reason_obj,
                message=req.comment or "",
            )
            log_kv(logger, "account.ReportPeer.ok", target=req.target, reason=type(reason_obj).__name__)
            return bool(res)
        except FloodWait as e:
            logger.warning("FloodWait %ss", e.value, extra={"trace_id": trace})
            await asyncio.sleep(int(e.value))
            return False
        except (PeerIdInvalid, ChannelInvalid, UserNotParticipant, ChatAdminRequired) as e:
            logger.error("ReportPeer failed: %s", type(e).__name__, extra={"trace_id": trace})
            return False
        except RPCError as e:
            logger.error("ReportPeer RPCError: %s", e, extra={"trace_id": trace})
            return False
        except Exception:
            logger.error("ReportPeer unexpected error", exc_info=True, extra={"trace_id": trace})
            return False

    @with_trace(__name__)
    async def run(self, req: ReportRequest) -> Tuple[int, int]:
        trace = get_trace_id()
        ok, fail = 0, 0
        loops = max(1, int(getattr(req, "report_count", 1)))
        log_kv(
            logger, "executor.run.start",
            loops=loops,
            target=req.target,
            reason=getattr(req.reason, "value", req.reason),
            ids=req.message_ids,
            delay=Config.DELAY_BETWEEN_REPORTS,
        )

        for i in range(1, loops + 1):
            logger.debug("executor.loop #%d/%d", i, loops, extra={"trace_id": trace})
            success = await (
                self._report_message(req)
                if (req.message_ids and len(req.message_ids) > 0)
                else self._report_peer(req)
            )
            if success:
                ok += 1
            else:
                fail += 1

            if i < loops and getattr(Config, "DELAY_BETWEEN_REPORTS", 0):
                await asyncio.sleep(float(Config.DELAY_BETWEEN_REPORTS))

        log_kv(logger, "executor.run.done", ok=ok, fail=fail)
        return ok, fail
