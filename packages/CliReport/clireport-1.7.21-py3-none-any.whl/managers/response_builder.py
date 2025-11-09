from core.models import ReportResult
from managers.report_manager import ReportManager

class ResponseBuilder:
    @staticmethod
    def build_summary_text(result: ReportResult) -> str:
        duration_str = ReportManager.format_duration(result.start_time, result.end_time)
        total = result.successful + result.failed
        efficiency = (result.successful / total * 100) if total else 0.0
        reason_name = ReportManager.get_persian_name(result.reason)
        comment = result.comment or "-"
        msg_ids = ",".join(map(str, result.message_ids)) if result.message_ids else "-"

        summary = (
            "📊 **گزارش عملیات گزارش‌دهی**\n\n"
            f"✅ **موفق:** `{result.successful}`\n"
            f"❌ **ناموفق:** `{result.failed}`\n"
            f"⏱️ **زمان اجرا:** `{duration_str}`\n"
            f"📈 **کارایی:** `{efficiency:.1f}%`\n"
            f"🎯 **هدف:** `{result.target}`\n"
            f"#️⃣ **آی‌دی پیام(ها):** `{msg_ids}`\n"
            f"🧩 **دلیل:** `{reason_name}`\n"
            f"📝 **توضیح:** `{comment}`\n"
        )
        return summary
