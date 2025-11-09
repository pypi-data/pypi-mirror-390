from core.models import ReportReason
from pyrogram.raw import types  # Kurigram فورک Pyrogram است و زیر همین namespace می‌آید.

def _t(name: str):
    return getattr(types, name, None)

_OTHER = types.InputReportReasonOther()

# مپ داینامیک: اگر کلاسی در بیلد فعلی نبود، به Other می‌افتد و خطا نمی‌دهد.
REASON_MAPPING = {
    ReportReason.SPAM:            (_t("InputReportReasonSpam") or (lambda: _OTHER))(),
    ReportReason.VIOLENCE:        (_t("InputReportReasonViolence") or (lambda: _OTHER))(),
    ReportReason.PORNOGRAPHY:     (_t("InputReportReasonPornography") or (lambda: _OTHER))(),
    ReportReason.CHILD_ABUSE:     (_t("InputReportReasonChildAbuse") or (lambda: _OTHER))(),
    ReportReason.ILLEGAL_DRUGS:   (_t("InputReportReasonIllegalDrugs") or (lambda: _OTHER))(),
    ReportReason.PERSONAL_DETAILS:(_t("InputReportReasonPersonalDetails") or (lambda: _OTHER))(),
    ReportReason.COPYRIGHT:       (_t("InputReportReasonCopyright") or (lambda: _OTHER))(),
    ReportReason.GEO_IRRELEVANT:  (_t("InputReportReasonGeoIrrelevant") or (lambda: _OTHER))(),
    ReportReason.SCAM:            (_t("InputReportReasonScam") or (lambda: _OTHER))(),
    ReportReason.FAKE:            (_t("InputReportReasonFake") or (lambda: _OTHER))(),
    ReportReason.OTHER:           _OTHER,
}

REASON_PERSIAN = {
    ReportReason.SPAM: "اسپم",
    ReportReason.VIOLENCE: "خشونت",
    ReportReason.PORNOGRAPHY: "محتوای جنسی بزرگسال",
    ReportReason.CHILD_ABUSE: "کودک‌آزاری",
    ReportReason.ILLEGAL_DRUGS: "مواد غیرقانونی",
    ReportReason.PERSONAL_DETAILS: "افشای اطلاعات شخصی",
    ReportReason.COPYRIGHT: "کپی‌رایت",
    ReportReason.GEO_IRRELEVANT: "نامرتبط با محل",
    ReportReason.SCAM: "کلاهبرداری/فیشینگ",
    ReportReason.FAKE: "جعل هویت/فیک",
    ReportReason.OTHER: "سایر",
}

# Aliasها (کلیدها lower-case) برای پوشش منوهای تلگرام؛ متن Alias به comment اضافه می‌شود.
ALIAS_TO_REASON = {
    "i don't like it": ("other", "User dislike"),
    "child abuse": ("child_abuse", ""),
    "child sexual abuse": ("child_abuse", "Child sexual abuse"),
    "child physical abuse": ("child_abuse", "Child physical abuse"),
    "violence": ("violence", ""),
    "graphic or disturbing content": ("violence", "Graphic/disturbing"),
    "extreme violence, dismemberment": ("violence", "Extreme violence/dismemberment"),
    "hate speech or symbols": ("violence", "Hate speech or symbols"),
    "calling for violence": ("violence", "Calling for violence"),
    "organized crime": ("violence", "Organized crime"),
    "terrorism": ("violence", "Terrorism"),
    "animal abuse": ("violence", "Animal abuse"),

    "illegal goods and services": ("other", "Illegal goods/services"),
    "weapons": ("other", "Weapons"),
    "drugs": ("illegal_drugs", "Drugs"),
    "fake documents": ("other", "Fake documents"),
    "counterfeit money": ("other", "Counterfeit money"),
    "hacking tools and malware": ("other", "Hacking tools/malware"),
    "counterfeit merchandise": ("other", "Counterfeit merchandise"),

    "illegal adult content": ("pornography", "Illegal adult content"),
    "copyrighted adult sexual imagery": ("copyright", "Copyrighted adult imagery"),
    "illegal sexual services": ("pornography", "Illegal sexual services"),
    "non-consensual sexual imagery": ("pornography", "Non-consensual sexual imagery"),
    "other illegal sexual content": ("pornography", "Other illegal sexual content"),

    "personal data": ("personal_details", ""),
    "private images": ("personal_details", "Private images"),
    "phone number": ("personal_details", "Phone number"),
    "address": ("personal_details", "Address"),
    "stolen data or credentials": ("personal_details", "Stolen data/credentials"),
    "other personal information": ("personal_details", "Other personal information"),

    "scam or fraud": ("scam", ""),
    "impersonation": ("fake", "Impersonation"),
    "deceptive or unrealistic financial claims": ("scam", "Deceptive financial claims"),
    "malware, phishing": ("scam", "Malware/phishing"),
    "fraudulent seller, product or service": ("scam", "Fraudulent seller/product/service"),

    "copyright": ("copyright", ""),
    "spam": ("spam", ""),
    "other": ("other", ""),
    "it's not illegal, but must be taken down": ("other", "Not illegal but must be removed"),
}
