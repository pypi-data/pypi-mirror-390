"""通用工具函数"""

from datetime import datetime, timezone


def get_datetime() -> dict:
    """Get current date and time with timezone"""
    utc_now = datetime.now(timezone.utc)
    system_tz = utc_now.astimezone().tzinfo
    return {
        "result": datetime.now(tz=system_tz).strftime("%Y-%m-%d %H:%M:%S %z")
    }
