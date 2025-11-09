from datetime import datetime
from core.models import ReportReason
from data.constants import REASON_PERSIAN
from utils.helpers import human_duration

class ReportManager:
    @staticmethod
    def get_persian_name(reason: ReportReason) -> str:
        return REASON_PERSIAN.get(reason, str(reason))

    @staticmethod
    def format_duration(start: datetime, end: datetime) -> str:
        return human_duration(end - start)
