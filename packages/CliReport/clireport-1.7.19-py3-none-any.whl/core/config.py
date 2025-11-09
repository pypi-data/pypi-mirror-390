# core/config.py
from __future__ import annotations

from typing import List


class Config:
    """
    تنظیمات ثابت برنامه (بدون وابستگی به متغیرهای محیطی).
    توجه: API_ID / API_HASH / ADMIN_IDS / SESSION_NAME عمداً ثابت و دست‌نخورده‌اند.
    """

    # --- هویت کلاینت تلگرام (همان مقادیر شما، تغییری ندهید) ---
    API_ID: int = 17221354
    API_HASH: str = "b86bbf4b700b4e922fff2c05b3b8985f"
    SESSION_NAME: str = "report_bot"
    ADMIN_IDS: List[int] = [5053851121]

    # --- تنظیمات گزارش ---
    # حداکثر تعداد ارسال گزارش در هر دستور
    MAX_REPORTS_PER_REQUEST: int = 10
    # تأخیر بین هر گزارش (ثانیه)
    DELAY_BETWEEN_REPORTS: int = 2
    # حداکثر طول کامنت
    MAX_COMMENT_LENGTH: int = 200
    # مهلتِ انتظار درخواست‌های حساس (ثانیه)
    REQUEST_TIMEOUT: int = 30

    # --- تنظیمات لاگ ---
    # سطح لاگ (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    LOG_LEVEL: str = "DEBUG"
    # فرمت لاگ (در صورت استفاده از لاگر داخلی پایتون)
    LOG_FORMAT: str = "%(asctime)s %(levelname)s %(name)s:%(lineno)d - %(message)s"

    # --- رفتار اجرای برنامه ---
    # ری‌استارت خودکار (اینجا ثابت: غیر فعال)
    AUTO_RESTART: bool = False

    @classmethod
    def validate(cls) -> None:
        """
        اعتبارسنجی حداقل‌ها؛ در صورت ایراد، خطا می‌دهد.
        """
        if not isinstance(cls.API_ID, int) or cls.API_ID <= 0:
            raise RuntimeError("API_ID باید عدد مثبت باشد.")
        if not isinstance(cls.API_HASH, str) or not cls.API_HASH.strip():
            raise RuntimeError("API_HASH تنظیم نشده است.")
        if not isinstance(cls.SESSION_NAME, str) or not cls.SESSION_NAME.strip():
            raise RuntimeError("SESSION_NAME نامعتبر است.")
        if not isinstance(cls.ADMIN_IDS, list) or not all(isinstance(x, int) for x in cls.ADMIN_IDS):
            raise RuntimeError("ADMIN_IDS باید لیست از اعداد کاربری باشد.")

        # کران‌های منطقی
        if cls.MAX_REPORTS_PER_REQUEST <= 0:
            cls.MAX_REPORTS_PER_REQUEST = 1
        if cls.DELAY_BETWEEN_REPORTS < 0:
            cls.DELAY_BETWEEN_REPORTS = 0
        if cls.MAX_COMMENT_LENGTH <= 0:
            cls.MAX_COMMENT_LENGTH = 200
        if cls.REQUEST_TIMEOUT <= 0:
            cls.REQUEST_TIMEOUT = 30
