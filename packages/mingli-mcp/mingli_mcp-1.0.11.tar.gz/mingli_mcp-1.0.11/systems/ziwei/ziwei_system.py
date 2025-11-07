"""
紫微斗数系统实现

基于iztro-py库实现紫微斗数排盘和分析
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional

from core.base_system import BaseFortuneSystem
from core.exceptions import DependencyError, SystemError, ValidationError

from .formatter import ZiweiFormatter

logger = logging.getLogger(__name__)

try:
    from iztro_py import astro

    IZTRO_AVAILABLE = True
except ImportError:
    logger.warning("iztro-py not installed, ZiweiSystem will not work")
    IZTRO_AVAILABLE = False
    astro = None  # type: ignore


class ZiweiSystem(BaseFortuneSystem):
    """紫微斗数系统实现"""

    # 十二宫位名称（中文）
    PALACES = [
        "命宫",
        "兄弟",
        "夫妻",
        "子女",
        "财帛",
        "疾厄",
        "迁移",
        "仆役",
        "官禄",
        "田宅",
        "福德",
        "父母",
    ]

    # 中英文宫位名称映射（iztro-py 使用英文名称）
    PALACE_NAME_MAP = {
        "命宫": "soulPalace",
        "兄弟": "siblingsPalace",
        "夫妻": "spousePalace",
        "子女": "childrenPalace",
        "财帛": "wealthPalace",
        "疾厄": "healthPalace",
        "迁移": "surfacePalace",
        "仆役": "friendsPalace",
        "官禄": "careerPalace",
        "田宅": "propertyPalace",
        "福德": "spiritPalace",
        "父母": "parentsPalace",
    }

    def __init__(self):
        if not IZTRO_AVAILABLE:
            raise DependencyError(
                "iztro-py library is not installed. Please install it with: pip install iztro-py"
            )
        self.formatter = ZiweiFormatter()

    def get_system_name(self) -> str:
        return "紫微斗数"

    def get_system_version(self) -> str:
        try:
            import iztro_py

            return getattr(iztro_py, "__version__", "0.1.0")
        except Exception:
            return "0.1.0"

    def _convert_datetime_for_horoscope(self, dt: datetime) -> tuple:
        """
        转换 datetime 为 iztro-py horoscope 方法所需格式

        Args:
            dt: datetime 对象

        Returns:
            (date_str, hour_index) 元组
            - date_str: "YYYY-M-D" 格式（月和日不补零）
            - hour_index: 时辰索引 0-11（每个时辰2小时）
        """
        # 格式化日期字符串，去掉月份和日期的前导零
        date_str = f"{dt.year}-{dt.month}-{dt.day}"

        # 计算时辰索引（0-11，每个时辰2小时）
        hour_index = dt.hour // 2

        return date_str, hour_index

    def get_chart(self, birth_info: Dict[str, Any], language: str = "zh-CN") -> Dict[str, Any]:
        """
        获取紫微斗数排盘

        Args:
            birth_info: 生辰信息
            language: 输出语言

        Returns:
            排盘详细信息
        """
        self.validate_birth_info(birth_info)

        try:
            # 根据历法类型调用不同的方法
            if birth_info.get("calendar", "solar") == "lunar":
                astrolabe = astro.by_lunar(
                    birth_info["date"],
                    birth_info["time_index"],
                    birth_info["gender"],
                    birth_info.get("is_leap_month", False),
                )
            else:
                astrolabe = astro.by_solar(
                    birth_info["date"], birth_info["time_index"], birth_info["gender"]
                )

            # 设置语言
            astrolabe.set_language(language)

            # 格式化输出
            return self.formatter.format_chart(astrolabe)

        except ValidationError:
            raise
        except ImportError as e:
            logger.error(f"Missing dependency for chart generation: {e}")
            raise DependencyError(f"依赖缺失: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error generating ziwei chart")
            raise SystemError(f"排盘失败: {str(e)}")

    def get_fortune(
        self,
        birth_info: Dict[str, Any],
        query_date: Optional[datetime] = None,
        language: str = "zh-CN",
    ) -> Dict[str, Any]:
        """
        获取紫微斗数运势（大限、流年、流月、流日、流时）

        Args:
            birth_info: 生辰信息
            query_date: 查询日期，默认当前时间
            language: 输出语言

        Returns:
            运势信息
        """
        self.validate_birth_info(birth_info)

        if query_date is None:
            query_date = datetime.now()

        try:
            # 先获取星盘
            if birth_info.get("calendar", "solar") == "lunar":
                astrolabe = astro.by_lunar(
                    birth_info["date"],
                    birth_info["time_index"],
                    birth_info["gender"],
                    birth_info.get("is_leap_month", False),
                )
            else:
                astrolabe = astro.by_solar(
                    birth_info["date"], birth_info["time_index"], birth_info["gender"]
                )

            # 设置语言
            astrolabe.set_language(language)

            # 获取运势（iztro-py 需要日期字符串和时辰索引）
            date_str, hour_index = self._convert_datetime_for_horoscope(query_date)
            horoscope = astrolabe.horoscope(date_str, hour_index)

            # 格式化输出
            return self.formatter.format_fortune(horoscope, query_date)

        except ValidationError:
            raise
        except ImportError as e:
            logger.error(f"Missing dependency for fortune generation: {e}")
            raise DependencyError(f"依赖缺失: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error generating ziwei fortune")
            raise SystemError(f"运势查询失败: {str(e)}")

    def analyze_palace(
        self, birth_info: Dict[str, Any], palace_name: str, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        分析特定宫位

        Args:
            birth_info: 生辰信息
            palace_name: 宫位名称（中文，如"命宫"）
            language: 输出语言

        Returns:
            宫位详细分析
        """
        if palace_name not in self.PALACES:
            raise ValidationError(
                f"无效的宫位名称: {palace_name}. 有效宫位: {', '.join(self.PALACES)}"
            )

        self.validate_birth_info(birth_info)

        try:
            # 获取完整星盘（formatter 已经将宫位名转换为中文）
            chart = self.get_chart(birth_info, language)

            # 找到指定宫位（直接匹配中文名）
            target_palace = None
            for palace in chart["palaces"]:
                if palace["name"] == palace_name:
                    target_palace = palace
                    break

            if target_palace is None:
                raise SystemError(f"未找到宫位: {palace_name}")

            # 格式化宫位分析
            return self.formatter.format_palace_analysis(target_palace, chart["basic_info"])

        except (ValidationError, SystemError):
            raise
        except Exception as e:
            logger.exception("Unexpected error analyzing palace")
            raise SystemError(f"宫位分析失败: {str(e)}")

    def get_supported_palaces(self) -> list:
        """返回支持的宫位列表"""
        return self.PALACES.copy()

    def get_capabilities(self) -> Dict[str, bool]:
        """返回系统功能支持"""
        return {
            "chart": True,
            "fortune": True,
            "palace_analysis": True,
            "compatibility": False,  # 暂不支持合盘
            "transit": False,  # 暂不支持推运
        }
