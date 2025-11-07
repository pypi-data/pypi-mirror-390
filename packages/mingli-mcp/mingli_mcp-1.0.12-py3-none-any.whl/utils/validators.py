"""
参数验证工具
"""

from datetime import datetime
from typing import Any


def validate_date(date_str: str) -> bool:
    """
    验证日期格式

    Args:
        date_str: 日期字符串 YYYY-MM-DD

    Returns:
        是否有效
    """
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_time_index(time_index: Any) -> bool:
    """
    验证时辰序号

    Args:
        time_index: 时辰序号

    Returns:
        是否有效
    """
    try:
        index = int(time_index)
        return 0 <= index <= 12
    except (ValueError, TypeError):
        return False


def validate_gender(gender: str) -> bool:
    """
    验证性别

    Args:
        gender: 性别字符串

    Returns:
        是否有效
    """
    return gender in ["男", "女"]
