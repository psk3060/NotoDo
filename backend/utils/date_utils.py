from datetime import datetime, timedelta, timezone

def ensure_utc(dt: datetime) -> datetime:
    """naive datetime이 들어오면 KST로 간주하고 UTC로 변환.
    (naive 값이 실제로 KST 벽시계 시간이라는 전제 하에)"""
    if dt.tzinfo is None:
        kst = timezone(timedelta(hours=9))
        dt = dt.replace(tzinfo=kst)
    return dt.astimezone(timezone.utc)