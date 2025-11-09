import re, shlex
from datetime import timedelta

def smart_split(s: str) -> list[str]:
    try:
        return shlex.split(s)
    except Exception:
        return s.strip().split()

def truncate_text(s: str, limit: int) -> str:
    s = s or ""
    return s if len(s) <= limit else s[: max(0, limit - 1)] + "…"

def escape_md(s: str) -> str:
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=\|\{\}\.\!])', r'\\\1', s)

def format_entity(entity: str) -> str:
    entity = entity.strip()
    entity = entity.replace("https://", "http://")
    entity = entity.replace("http://t.me/", "t.me/")
    return entity

def validate_t_me_link(entity: str) -> bool:
    # اجازه به: @user | t.me/user | t.me/user/msg | t.me/c/chat/msg
    return bool(re.match(r"^(?:@[\w\d_]{5,}|t\.me/(?:c/\d+/\d+|[\w\d_]{5,}(?:/\d+)?))$", entity))

def parse_entity_and_message_id(entity: str):
    """
    ورودی: @user | t.me/user | t.me/user/123 | t.me/c/111/222
    خروجی: (entity_norm, message_id or None)
    """
    entity = format_entity(entity)

    # t.me/c/<chat>/<msg>
    m = re.match(r"^t\.me/c/(\d+)/(\d+)$", entity)
    if m:
        chat_id = m.group(1)
        msg_id = int(m.group(2))
        return f"t.me/c/{chat_id}", msg_id

    # t.me/<username>/<msgid>
    m = re.match(r"^t\.me/([\w\d_]{5,})/(\d+)$", entity)
    if m:
        username = m.group(1)
        msg_id = int(m.group(2))
        return f"t.me/{username}", msg_id

    # t.me/<username>
    m = re.match(r"^t\.me/([\w\d_]{5,})$", entity)
    if m:
        return f"t.me/{m.group(1)}", None

    # @username
    m = re.match(r"^@([\w\d_]{5,})$", entity)
    if m:
        return f"@{m.group(1)}", None

    return entity, None

def parse_message_ids(token: str) -> list[int] | None:
    """
    '8' یا '8,12,19' → [8,12,19]
    """
    token = (token or "").strip().strip(",")
    if not token:
        return None
    parts = [p for p in token.split(",") if p.strip()]
    try:
        return [int(p) for p in parts]
    except Exception:
        return None

def human_duration(delta: timedelta) -> str:
    secs = int(delta.total_seconds())
    m, s = divmod(secs, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
