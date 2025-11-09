# core/executor.py
from __future__ import annotations

import asyncio
import inspect
import logging
from time import perf_counter
from typing import Tuple, Dict, Any, Iterable

from pyrogram import Client
from pyrogram.errors import (
    FloodWait, PeerIdInvalid, ChannelInvalid, UserNotParticipant, ChatAdminRequired, RPCError
)
from pyrogram.raw import functions, types  # ⬅️ انواع ReportResult و MessageReportOption اینجاست

from core.models import ReportRequest
from data.constants import REASON_MAPPING
from core.config import Config

from logkit import get_trace_id, with_trace, log_kv

logger = logging.getLogger(__name__)

# --- کمک‌تابع: بهترین گزینه‌ی منو را بر اساس reason حدس بزن ---
def _pick_option_by_reason(reason_value: str, options: Iterable[types.MessageReportOption]) -> bytes | None:
    """
    تلاش می‌کند گزینه‌ای را که با reason ما هم‌خوان است برگرداند (فیلد .option به صورت bytes).
    """
    r = (reason_value or "").lower()
    # کلیدواژه‌های ساده برای مَچ
    keywords = {
        "spam": ["spam", "advert", "ads", "promo"],
        "violence": ["violence", "harm", "threat"],
        "pornography": ["porn", "sexual", "adult"],
        "child_abuse": ["child", "minor"],
        "illegal_drugs": ["drug", "narcotic"],
        "personal_details": ["personal", "private", "dox"],
        "copyright": ["copyright", "dmca"],
        "geo_irrelevant": ["geo", "location", "irrelevant"],
        "scam": ["scam", "fraud", "phish"],
        "fake": ["fake", "impersonat", "misleading"],
        "other": ["other", "misc"],
    }
    keys = keywords.get(r, []) + [r]  # خود reason هم به آخر لیست اضافه شود
    for opt in options or []:
        text = (getattr(opt, "text", "") or "").lower()
        if any(k in text for k in keys):
            return getattr(opt, "option", None)
    # اگر هیچ‌کدام نخورد، اولی را بدهیم (به‌عنوان fallback)
    first = next(iter(options), None)
    return getattr(first, "option", None) if first else None


async def _safe_invoke(client: Client, func_cls, **kwargs) -> Any:
    """
    نسخه‌ی ساده‌تر: کلاسِ RAW را مستقیم با کلیدهای صحیح صدا می‌زنیم؛
    (به‌جای مپِ تطبیقی) چون الان امضای جدید را می‌دانیم.
    """
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
        گزارش روی پیام(ها) — مطابق Layer 214:
        messages.report(peer, id[], option: bytes, message: str) -> ReportResult
        جریان: empty option -> choose option (optional) -> add comment (optional)
        """
        trace = get_trace_id()
        peer = await self.client.resolve_peer(req.target)
        ids = req.message_ids or []
        comment = req.comment or ""
        reason_val = getattr(req.reason, "value", str(req.reason)).lower()

        # 1) مرحله اول: option = b""  (خالی)
        try:
            logger.debug(
                "messages.Report stage1 → peer=%r ids=%r option=%r comment_len=%d",
                req.target, ids, b"", len(comment),
                extra={"trace_id": trace},
            )
            res = await _safe_invoke(
                self.client,
                functions.messages.Report,
                peer=peer,
                id=ids,
                option=b"",
                message=comment,
            )
        except FloodWait as e:
            logger.warning("FloodWait %ss", e.value, extra={"trace_id": trace})
            await asyncio.sleep(int(e.value))
            return False
        except (PeerIdInvalid, ChannelInvalid, UserNotParticipant, ChatAdminRequired) as e:
            logger.error("messages.Report stage1 failed: %s", type(e).__name__, extra={"trace_id": trace})
            return False
        except RPCError as e:
            logger.error("messages.Report stage1 RPCError: %s", e, extra={"trace_id": trace})
            return False
        except Exception:
            logger.error("messages.Report stage1 unexpected", exc_info=True, extra={"trace_id": trace})
            return False

        # 2) تفسیر نتیجه
        if isinstance(res, types.ReportResultReported):
            log_kv(logger, "messages.Report.reported", target=req.target, ids=ids)
            return True

        if isinstance(res, types.ReportResultChooseOption):
            # باید یکی از گزینه‌ها را انتخاب کنیم
            picked = _pick_option_by_reason(reason_val, res.options)
            if not picked:
                logger.error("no matching option for reason=%r", reason_val, extra={"trace_id": trace})
                return False

            logger.debug(
                "messages.Report stage2 choose → picked=%r (title=%r)", picked, getattr(res, "title", None),
                extra={"trace_id": trace},
            )
            try:
                res2 = await _safe_invoke(
                    self.client,
                    functions.messages.Report,
                    peer=peer,
                    id=ids,
                    option=picked,
                    message=comment,
                )
            except Exception:
                logger.error("messages.Report stage2 choose failed", exc_info=True, extra={"trace_id": trace})
                return False

            if isinstance(res2, types.ReportResultReported):
                log_kv(logger, "messages.Report.reported", target=req.target, ids=ids)
                return True
            if isinstance(res2, types.ReportResultAddComment):
                # باید با همین option یک بار دیگر با comment بفرستیم
                final_comment = comment or reason_val
                logger.debug("messages.Report stage3 add_comment → comment_len=%d", len(final_comment), extra={"trace_id": trace})
                try:
                    res3 = await _safe_invoke(
                        self.client,
                        functions.messages.Report,
                        peer=peer,
                        id=ids,
                        option=res2.option,
                        message=final_comment,
                    )
                except Exception:
                    logger.error("messages.Report stage3 add_comment failed", exc_info=True, extra={"trace_id": trace})
                    return False
                ok = isinstance(res3, types.ReportResultReported)
                log_kv(logger, "messages.Report.final", ok=ok)
                return bool(ok)

            # هر نتیجه‌ی دیگری غیرمنتظره است
            logger.error("unexpected ReportResult after choose: %r", type(res2).__name__, extra={"trace_id": trace})
            return False

        if isinstance(res, types.ReportResultAddComment):
            # مستقیم از ما کامنت خواسته؛ option در خود result هست
            final_comment = comment or reason_val
            logger.debug("messages.Report stage2 add_comment → comment_len=%d", len(final_comment), extra={"trace_id": trace})
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
                logger.error("messages.Report stage2 add_comment failed", exc_info=True, extra={"trace_id": trace})
                return False
            ok = isinstance(res2, types.ReportResultReported)
            log_kv(logger, "messages.Report.final", ok=ok)
            return bool(ok)

        logger.error("unexpected ReportResult type: %r", type(res).__name__, extra={"trace_id": trace})
        return False

    @with_trace(__name__)
    async def _report_peer(self, req: ReportRequest) -> bool:
        """
        گزارش روی خودِ peer (بدون message_id) — طبق مستندات فعلی بدون تغییر.
        """
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
