"""
生辰信息数据模型
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class BirthInfo:
    """生辰信息数据类"""

    date: str  # YYYY-MM-DD格式
    time_index: int  # 0-12，对应子时到晚子时
    gender: str  # "男" 或 "女"
    calendar: str = "solar"  # "solar" 或 "lunar"
    is_leap_month: bool = False  # 是否闰月（仅农历有效）

    def __post_init__(self):
        """验证数据有效性"""
        if not 0 <= self.time_index <= 12:
            raise ValueError("时辰序号必须在0-12之间")

        if self.gender not in ["男", "女"]:
            raise ValueError("性别必须是'男'或'女'")

        if self.calendar not in ["solar", "lunar"]:
            raise ValueError("历法类型必须是'solar'或'lunar'")

        # 验证日期格式
        try:
            datetime.strptime(self.date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("日期格式必须是YYYY-MM-DD")

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "date": self.date,
            "time_index": self.time_index,
            "gender": self.gender,
            "calendar": self.calendar,
            "is_leap_month": self.is_leap_month,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BirthInfo":
        """从字典创建"""
        return cls(
            date=data["date"],
            time_index=data["time_index"],
            gender=data["gender"],
            calendar=data.get("calendar", "solar"),
            is_leap_month=data.get("is_leap_month", False),
        )

    def get_time_range(self) -> str:
        """获取时辰对应的时间段"""
        time_ranges = [
            "23:00~01:00",  # 0 早子时
            "01:00~03:00",  # 1 丑时
            "03:00~05:00",  # 2 寅时
            "05:00~07:00",  # 3 卯时
            "07:00~09:00",  # 4 辰时
            "09:00~11:00",  # 5 巳时
            "11:00~13:00",  # 6 午时
            "13:00~15:00",  # 7 未时
            "15:00~17:00",  # 8 申时
            "17:00~19:00",  # 9 酉时
            "19:00~21:00",  # 10 戌时
            "21:00~23:00",  # 11 亥时
            "23:00~01:00",  # 12 晚子时
        ]
        return time_ranges[self.time_index]

    def get_time_name(self) -> str:
        """获取时辰名称"""
        time_names = [
            "早子时",
            "丑时",
            "寅时",
            "卯时",
            "辰时",
            "巳时",
            "午时",
            "未时",
            "申时",
            "酉时",
            "戌时",
            "亥时",
            "晚子时",
        ]
        return time_names[self.time_index]
