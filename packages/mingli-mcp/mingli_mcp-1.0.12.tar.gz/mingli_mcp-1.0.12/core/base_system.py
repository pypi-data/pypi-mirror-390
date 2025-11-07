"""
命理系统抽象基类

定义统一的接口，支持不同命理系统（紫微、八字、占星等）
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from .exceptions import ValidationError


class BaseFortuneSystem(ABC):
    """命理系统抽象基类"""

    @abstractmethod
    def get_system_name(self) -> str:
        """
        返回系统名称

        Returns:
            系统名称，如 "紫微斗数"、"八字"、"西方占星"
        """
        pass

    @abstractmethod
    def get_system_version(self) -> str:
        """
        返回系统版本

        Returns:
            版本号字符串
        """
        pass

    @abstractmethod
    def get_chart(self, birth_info: Dict[str, Any], language: str = "zh-CN") -> Dict[str, Any]:
        """
        获取排盘信息

        Args:
            birth_info: 生辰信息字典，包含以下字段：
                - date: 日期 (str格式 YYYY-MM-DD 或 datetime对象)
                - time_index: 时辰序号 (int, 0-12)
                - gender: 性别 (str, "男"/"女")
                - calendar: 历法 (str, "solar"/"lunar", 默认"solar")
                - is_leap_month: 是否闰月 (bool, 默认False, 仅农历有效)
            language: 输出语言 (str, 默认"zh-CN")
                支持: zh-CN, zh-TW, en-US, ja-JP, ko-KR, vi-VN

        Returns:
            排盘详细信息字典，包含：
                - system: 系统名称
                - basic_info: 基本信息（日期、时辰、星座等）
                - palaces/houses: 宫位信息
                - stars: 星曜信息
                - elements: 五行信息
                - ... (各系统特有数据)

        Raises:
            ValueError: 参数格式错误
            RuntimeError: 排盘计算错误
        """
        pass

    @abstractmethod
    def get_fortune(
        self,
        birth_info: Dict[str, Any],
        query_date: Optional[datetime] = None,
        language: str = "zh-CN",
    ) -> Dict[str, Any]:
        """
        获取运势信息

        Args:
            birth_info: 生辰信息字典（同get_chart）
            query_date: 查询日期，默认为当前时间
            language: 输出语言 (str, 默认"zh-CN")
                支持: zh-CN, zh-TW, en-US, ja-JP, ko-KR, vi-VN

        Returns:
            运势信息字典，可能包含：
                - decadal: 大限（紫微）
                - yearly: 流年
                - monthly: 流月
                - daily: 流日
                - ... (各系统特有运势)

        Raises:
            ValueError: 参数错误
            RuntimeError: 运势计算错误
        """
        pass

    @abstractmethod
    def analyze_palace(
        self, birth_info: Dict[str, Any], palace_name: str, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        分析特定宫位的详细信息

        Args:
            birth_info: 生辰信息字典
            palace_name: 宫位名称（各系统定义不同）
            language: 输出语言 (str, 默认"zh-CN")
                支持: zh-CN, zh-TW, en-US, ja-JP, ko-KR, vi-VN

        Returns:
            宫位详细分析字典，包含：
                - palace_name: 宫位名称
                - basic_info: 基本信息
                - stars: 该宫位的星曜
                - interpretation: 解读信息（可选）

        Raises:
            ValueError: 宫位名称无效
        """
        pass

    def validate_birth_info(self, birth_info: Dict[str, Any]) -> None:
        """
        验证生辰信息的有效性

        Args:
            birth_info: 生辰信息字典

        Raises:
            ValidationError: 参数无效或缺失
        """
        required_fields = ["date", "time_index", "gender"]
        for field in required_fields:
            if field not in birth_info:
                raise ValidationError(f"缺少必需字段: {field}")

        # 验证时辰
        if not 0 <= birth_info["time_index"] <= 12:
            raise ValidationError("时辰序号必须在0-12之间")

        # 验证性别
        if birth_info["gender"] not in ["男", "女"]:
            raise ValidationError("性别必须是'男'或'女'")

    def get_supported_palaces(self) -> list:
        """
        返回该系统支持的宫位列表

        Returns:
            宫位名称列表
        """
        return []

    def get_capabilities(self) -> Dict[str, bool]:
        """
        返回系统支持的功能

        Returns:
            功能字典，例如：
            {
                'chart': True,
                'fortune': True,
                'palace_analysis': True,
                'compatibility': False,
                ...
            }
        """
        return {
            "chart": True,
            "fortune": False,
            "palace_analysis": False,
            "compatibility": False,
        }
