# core/executor.py
from __future__ import annotations

import asyncio
import inspect
import logging
from time import perf_counter
from typing import Tuple, Dict, Any

from pyrogram import Client
from pyrogram.errors import (
    FloodWait, PeerIdInvalid, ChannelInvalid, UserNotParticipant, ChatAdminRequired, RPCError
)
from pyrogram.raw import functions

from core.models import ReportRequest
from data.constants import REASON_MAPPING
from core.config import Config

# ---- لاگ‌گیری سرتاسری از پوشه‌ی CliReport/logging ----
from CliReport.logkit import get_trace_id, with_trace, log_kv

logger = logging.getLogger(__name__)


def _build_kwargs(signature_params: Dict[str, Any], wanted: Dict[str, Any]) -> Dict[str, Any]:
    """
    مپ‌کردن کلیدهای استاندارد ما به کلیدهای واقعی سازنده‌ی کلاس raw در نسخه‌ی فعلی.
    """
    trace = get_trace_id()
    params = set(signature_params.keys()) if signature_params else set()
    kw: Dict[str, Any] = {}

    # peer
    for k in ("peer", "peer_", "input_peer"):
        if k in params and "peer" in wanted:
            kw[k] = wanted["peer"]
            logger.debug("kwargs map: peer → %s", k, extra={"trace_id": trace})
            break

    # id(s)
    for k in ("id", "ids", "messages", "message_ids"):
        if k in params and "id" in wanted:
            kw[k] = wanted["id"]
            logger.debug("kwargs map: id → %s", k, extra={"trace_id": trace})
            break

    # reason
    for k in ("reason", "reason_", "report_reason"):
        if k in params and "reason" in wanted:
            kw[k] = wanted["reason"]
            logger.debug("kwargs map: reason → %s", k, extra={"trace_id": trace})
            break

    # message/comment
    for k in ("message", "comment", "msg", "text"):
        if k in params and "message" in wanted:
            kw[k] = wanted["message"]
            logger.debug("kwargs map: message → %s", k, extra={"trace_id": trace})
            break

    logger.debug(
        "kwargs result keys=%r missing_from_sig=%r",
        list(kw.keys()),
        [k for k in wanted.keys() if k not in {"peer", "id", "reason", "message"}],
        extra={"trace_id": trace},
    )
    return kw


async def _safe_invoke(client: Client, func_cls, wanted_kwargs: Dict[str, Any]) -> None:
    """
    فراخوانی سازگار با نسخه: امضای func_cls را می‌خواند و kwargs سازگار می‌سازد.
    """
    trace = get_trace_id()
    func_name = getattr(func_cls, "__name__", str(func_cls))
    start = perf_counter()

    # امضا را به‌صورت امن بخوانیم
    try:
        sig = getattr(func_cls, "__signature__", None) or getattr(func_cls.__init__, "__signature__", None)
        if sig is None:
            try:
                sig = inspect.signature(func_cls)
            except Exception:
                sig = None
        params = sig.parameters if sig is not None else {}
        logger.debug(
            "invoke.prepare func=%s sig_params=%r wanted_keys=%r",
            func_name, list(params.keys()) if params else None, list(wanted_kwargs.keys()),
            extra={"trace_id": trace},
        )
    except Exception:
        logger.exception("could not inspect signature for %s", func_name, extra={"trace_id": trace})
        params = {}

    # مپ سازگار
    kwargs = _build_kwargs(params, wanted_kwargs) if params else {}
    if not kwargs:
        # آخرین تلاش: همان کلیدهای استاندارد
        kwargs = dict(wanted_kwargs)
        logger.debug("invoke.prepare: fallback to wanted_kwargs", extra={"trace_id": trace})

    # خود فراخوانی
    try:
        logger.debug("invoke.call func=%s kwargs_keys=%r", func_name, list(kwargs.keys()), extra={"trace_id": trace})
        await client.invoke(func_cls(**kwargs))
        dur = (perf_counter() - start) * 1000
        logger.info("invoke.ok func=%s (%.1f ms)", func_name, dur, extra={"trace_id": trace})
    except Exception:
        dur = (perf_counter() - start) * 1000
        logger.exception("invoke.failed func=%s (%.1f ms)", func_name, dur, extra={"trace_id": trace})
        raise


class ReportExecutor:
    def __init__(self, client: Client):
        self.client = client

    @with_trace(__name__)
    async def _report_message(self, req: ReportRequest) -> bool:
        """
        گزارش روی پیام(ها)
        """
        trace = get_trace_id()
        # resolve peer (ممکن است استثنا بدهد)
        peer = await self.client.resolve_peer(req.target)

        reason_obj = REASON_MAPPING[req.reason]  # باید instance از InputReportReason* باشد
        wanted = {
            "peer": peer,
            "id": req.message_ids or [],
            "reason": reason_obj,
            "message": req.comment or "",
        }

        logger.debug(
            "messages.Report → target=%r ids=%r reason=%s comment_len=%d",
            req.target, req.message_ids, type(reason_obj).__name__, len(req.comment or ""),
            extra={"trace_id": trace},
        )

        try:
            await _safe_invoke(self.client, functions.messages.Report, wanted)
            log_kv(
                logger, "messages.Report.ok",
                target=req.target,
                ids=req.message_ids,
                reason=type(reason_obj).__name__,
            )
            return True

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
            logger.error("messages.Report unexpected error", exc_info=True, extra={"trace_id": trace})
            return False

    @with_trace(__name__)
    async def _report_peer(self, req: ReportRequest) -> bool:
        """
        گزارش روی خودِ peer (بدون message_id)
        """
        trace = get_trace_id()
        peer = await self.client.resolve_peer(req.target)

        reason_obj = REASON_MAPPING[req.reason]
        wanted = {
            "peer": peer,
            "reason": reason_obj,
            "message": req.comment or "",
        }

        logger.debug(
            "account.ReportPeer → target=%r reason=%s comment_len=%d",
            req.target, type(reason_obj).__name__, len(req.comment or ""),
            extra={"trace_id": trace},
        )

        try:
            await _safe_invoke(self.client, functions.account.ReportPeer, wanted)
            log_kv(
                logger, "account.ReportPeer.ok",
                target=req.target,
                reason=type(reason_obj).__name__,
            )
            return True

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
        """
        اجرای چندبارهٔ گزارش طبق report_count
        خروجی: (ok, fail)
        """
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

            # فاصله بین گزارش‌ها
            delay = float(getattr(Config, "DELAY_BETWEEN_REPORTS", 0) or 0)
            if i < loops and delay > 0:
                await asyncio.sleep(delay)

        log_kv(logger, "executor.run.done", ok=ok, fail=fail)
        return ok, fail
