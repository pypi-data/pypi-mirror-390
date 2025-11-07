"""
八字系统实现

基于lunar_python库实现八字（四柱命理）排盘和分析
参考: https://github.com/china-testing/bazi
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

from core.base_system import BaseFortuneSystem
from core.exceptions import DependencyError, SystemError, ValidationError

from .formatter import BaziFormatter

logger = logging.getLogger(__name__)

try:
    from lunar_python import Lunar, Solar

    LUNAR_AVAILABLE = True
except ImportError:
    logger.warning("lunar_python not installed, BaziSystem will not work")
    LUNAR_AVAILABLE = False
    if not TYPE_CHECKING:
        Lunar = None  # type: ignore
        Solar = None  # type: ignore


class BaziSystem(BaseFortuneSystem):
    """八字系统实现"""

    # 十天干
    GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

    # 十二地支
    ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

    # 五行属性
    WU_XING = {
        "金": "庚辛申酉",
        "木": "甲乙寅卯",
        "水": "壬癸子亥",
        "火": "丙丁巳午",
        "土": "戊己丑辰未戌",
    }

    # 十神对应关系（以日干为主）
    TEN_DEITIES = {
        "甲": {
            "甲": "比肩",
            "乙": "劫财",
            "丙": "食神",
            "丁": "伤官",
            "戊": "偏财",
            "己": "正财",
            "庚": "七杀",
            "辛": "正官",
            "壬": "偏印",
            "癸": "正印",
        },
        "乙": {
            "甲": "劫财",
            "乙": "比肩",
            "丙": "伤官",
            "丁": "食神",
            "戊": "正财",
            "己": "偏财",
            "庚": "正官",
            "辛": "七杀",
            "壬": "正印",
            "癸": "偏印",
        },
        "丙": {
            "丙": "比肩",
            "丁": "劫财",
            "戊": "食神",
            "己": "伤官",
            "庚": "偏财",
            "辛": "正财",
            "壬": "七杀",
            "癸": "正官",
            "甲": "偏印",
            "乙": "正印",
        },
        "丁": {
            "丙": "劫财",
            "丁": "比肩",
            "戊": "伤官",
            "己": "食神",
            "庚": "正财",
            "辛": "偏财",
            "壬": "正官",
            "癸": "七杀",
            "甲": "正印",
            "乙": "偏印",
        },
        "戊": {
            "戊": "比肩",
            "己": "劫财",
            "庚": "食神",
            "辛": "伤官",
            "壬": "偏财",
            "癸": "正财",
            "甲": "七杀",
            "乙": "正官",
            "丙": "偏印",
            "丁": "正印",
        },
        "己": {
            "戊": "劫财",
            "己": "比肩",
            "庚": "伤官",
            "辛": "食神",
            "壬": "正财",
            "癸": "偏财",
            "甲": "正官",
            "乙": "七杀",
            "丙": "正印",
            "丁": "偏印",
        },
        "庚": {
            "庚": "比肩",
            "辛": "劫财",
            "壬": "食神",
            "癸": "伤官",
            "甲": "偏财",
            "乙": "正财",
            "丙": "七杀",
            "丁": "正官",
            "戊": "偏印",
            "己": "正印",
        },
        "辛": {
            "庚": "劫财",
            "辛": "比肩",
            "壬": "伤官",
            "癸": "食神",
            "甲": "正财",
            "乙": "偏财",
            "丙": "正官",
            "丁": "七杀",
            "戊": "正印",
            "己": "偏印",
        },
        "壬": {
            "壬": "比肩",
            "癸": "劫财",
            "甲": "食神",
            "乙": "伤官",
            "丙": "偏财",
            "丁": "正财",
            "戊": "七杀",
            "己": "正官",
            "庚": "偏印",
            "辛": "正印",
        },
        "癸": {
            "壬": "劫财",
            "癸": "比肩",
            "甲": "伤官",
            "乙": "食神",
            "丙": "正财",
            "丁": "偏财",
            "戊": "正官",
            "己": "七杀",
            "庚": "正印",
            "辛": "偏印",
        },
    }

    # 地支藏干
    ZHI_CANG_GAN = {
        "子": ["癸"],
        "丑": ["己", "癸", "辛"],
        "寅": ["甲", "丙", "戊"],
        "卯": ["乙"],
        "辰": ["戊", "乙", "癸"],
        "巳": ["丙", "戊", "庚"],
        "午": ["丁", "己"],
        "未": ["己", "丁", "乙"],
        "申": ["庚", "壬", "戊"],
        "酉": ["辛"],
        "戌": ["戊", "辛", "丁"],
        "亥": ["壬", "甲"],
    }

    def __init__(self):
        if not LUNAR_AVAILABLE:
            raise DependencyError(
                "lunar_python library is not installed. Please install it with: pip install lunar_python"
            )
        self.formatter = BaziFormatter()

    def get_system_name(self) -> str:
        return "八字"

    def get_system_version(self) -> str:
        return "1.0.0"

    def get_chart(self, birth_info: Dict[str, Any], language: str = "zh-CN") -> Dict[str, Any]:
        """
        获取八字排盘

        Args:
            birth_info: 生辰信息，包含:
                - date: 日期 (YYYY-MM-DD)
                - time_index: 时辰序号 (0-12)，或者使用 hour 指定具体小时
                - gender: 性别 (男/女)
                - calendar: 历法 (solar/lunar)，默认solar
                - is_leap_month: 是否闰月（仅农历），默认False
            language: 输出语言（暂未实现，保留接口一致性）

        Returns:
            八字排盘详细信息
        """
        self.validate_birth_info(birth_info)
        # Note: lunar_python doesn't support i18n yet, language parameter is ignored for now

        try:
            # 获取lunar对象
            lunar = self._get_lunar_object(birth_info)

            # 提取四柱
            year_pillar = lunar.getYearInGanZhi()
            month_pillar = lunar.getMonthInGanZhi()
            day_pillar = lunar.getDayInGanZhi()
            hour_pillar = lunar.getTimeInGanZhi()

            # 分解天干地支
            year_gan, year_zhi = year_pillar[0], year_pillar[1]
            month_gan, month_zhi = month_pillar[0], month_pillar[1]
            day_gan, day_zhi = day_pillar[0], day_pillar[1]
            hour_gan, hour_zhi = hour_pillar[0], hour_pillar[1]

            # 计算十神
            deities = self._calculate_ten_deities(
                day_gan,
                [year_gan, month_gan, day_gan, hour_gan, year_zhi, month_zhi, day_zhi, hour_zhi],
            )

            # 计算五行
            wu_xing = self._calculate_wu_xing(
                [year_gan, month_gan, day_gan, hour_gan, year_zhi, month_zhi, day_zhi, hour_zhi]
            )

            # 构建结果
            result = {
                "solar_date": birth_info["date"],
                "lunar_date": lunar.toString(),
                "gender": birth_info["gender"],
                "pillars": {
                    "year": {"gan": year_gan, "zhi": year_zhi, "pillar": year_pillar},
                    "month": {"gan": month_gan, "zhi": month_zhi, "pillar": month_pillar},
                    "day": {"gan": day_gan, "zhi": day_zhi, "pillar": day_pillar},
                    "hour": {"gan": hour_gan, "zhi": hour_zhi, "pillar": hour_pillar},
                },
                "eight_char": f"{year_pillar} {month_pillar} {day_pillar} {hour_pillar}",
                "zodiac": lunar.getYearShengXiao(),
                "deities": deities,
                "wu_xing": wu_xing,
                "zhi_cang_gan": self._get_zhi_cang_gan(year_zhi, month_zhi, day_zhi, hour_zhi),
                "day_master": day_gan,  # 日主（日干）
            }

            return result

        except ValidationError:
            raise
        except (ImportError, AttributeError) as e:
            logger.error(f"Missing dependency for chart generation: {e}")
            raise DependencyError(f"依赖缺失: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error generating bazi chart")
            raise SystemError(f"八字排盘失败: {str(e)}")

    def get_fortune(
        self,
        birth_info: Dict[str, Any],
        query_date: Optional[datetime] = None,
        language: str = "zh-CN",
    ) -> Dict[str, Any]:
        """
        获取八字运势（大运、流年）

        Args:
            birth_info: 生辰信息
            query_date: 查询日期，默认当前时间
            language: 输出语言（暂未实现，保留接口一致性）

        Returns:
            运势信息
        """
        self.validate_birth_info(birth_info)
        # Note: lunar_python doesn't support i18n yet, language parameter is ignored for now

        if query_date is None:
            query_date = datetime.now()

        try:
            # 获取基本八字
            chart = self.get_chart(birth_info, language)

            # 计算年龄
            birth_year = int(birth_info["date"].split("-")[0])
            current_year = query_date.year
            age = current_year - birth_year

            # 计算大运（简化版，每10年一个大运）
            da_yun_index = age // 10

            # 获取流年天干地支
            query_solar = Solar.fromDate(query_date)
            query_lunar = query_solar.getLunar()
            liu_nian_gan_zhi = query_lunar.getYearInGanZhi()

            result = {
                "query_date": query_date.strftime("%Y-%m-%d"),
                "age": age,
                "day_master": chart["day_master"],
                "da_yun": {
                    "index": da_yun_index,
                    "age_range": f"{da_yun_index * 10}-{(da_yun_index + 1) * 10 - 1}岁",
                    "description": f"第{da_yun_index + 1}个大运",
                },
                "liu_nian": {
                    "year": current_year,
                    "gan_zhi": liu_nian_gan_zhi,
                    "zodiac": query_lunar.getYearShengXiao(),
                },
                "basic_chart": chart,
            }

            return result

        except ValidationError:
            raise
        except (ImportError, AttributeError) as e:
            logger.error(f"Missing dependency for fortune generation: {e}")
            raise DependencyError(f"依赖缺失: {str(e)}")
        except Exception as e:
            logger.exception("Unexpected error calculating bazi fortune")
            raise SystemError(f"运势计算失败: {str(e)}")

    def analyze_element(self, birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析五行强弱

        Args:
            birth_info: 生辰信息

        Returns:
            五行分析结果
        """
        try:
            chart = self.get_chart(birth_info)
            wu_xing = chart["wu_xing"]

            # 计算总分
            total = sum(wu_xing["scores"].values())

            # 计算百分比
            percentages = {
                element: (score / total * 100 if total > 0 else 0)
                for element, score in wu_xing["scores"].items()
            }

            # 找出最强和最弱的五行
            strongest = max(wu_xing["scores"].items(), key=lambda x: x[1])
            weakest = min(wu_xing["scores"].items(), key=lambda x: x[1])

            # 五行缺失
            missing = [elem for elem, score in wu_xing["scores"].items() if score == 0]

            result = {
                "scores": wu_xing["scores"],
                "percentages": percentages,
                "strongest": {"element": strongest[0], "score": strongest[1]},
                "weakest": {"element": weakest[0], "score": weakest[1]},
                "missing": missing,
                "balance": self._judge_balance(wu_xing["scores"]),
                "day_master": chart["day_master"],
                "day_master_element": self._get_element(chart["day_master"]),
            }

            return result

        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Unexpected error analyzing wu xing")
            raise SystemError(f"五行分析失败: {str(e)}")

    def _get_lunar_object(self, birth_info: Dict[str, Any]) -> Lunar:
        """获取lunar对象"""
        date_str = birth_info["date"]
        year, month, day = map(int, date_str.split("-"))

        # 计算小时
        if "hour" in birth_info:
            hour = birth_info["hour"]
        elif "time_index" in birth_info:
            time_index = birth_info["time_index"]
            # 时辰对应关系：0=早子时(0点), 1=丑时(1点), ... 12=晚子时(23点)
            # 简化处理：每个时辰2小时，从早子时23点开始
            if time_index == 0:
                hour = 0  # 早子时 23-1点，用0点代表
            else:
                hour = (time_index - 1) * 2 + 1  # 其他时辰
        else:
            hour = 0  # 默认子时

        if birth_info.get("calendar", "solar") == "lunar":
            # 农历
            lunar = Lunar.fromYmd(year, month, day)
            # lunar_python 需要用Solar来设置时间
            solar = Solar.fromYmdHms(
                lunar.getSolar().getYear(),
                lunar.getSolar().getMonth(),
                lunar.getSolar().getDay(),
                hour,
                0,
                0,
            )
            return solar.getLunar()
        else:
            # 阳历
            solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
            return solar.getLunar()

    def _calculate_ten_deities(self, day_gan: str, chars: list) -> Dict:
        """计算十神"""
        if day_gan not in self.TEN_DEITIES:
            return {}

        deity_map = self.TEN_DEITIES[day_gan]

        return {
            "year_gan": deity_map.get(chars[0], "未知"),
            "month_gan": deity_map.get(chars[1], "未知"),
            "day_gan": deity_map.get(chars[2], "未知"),
            "hour_gan": deity_map.get(chars[3], "未知"),
            # 地支中的藏干也需要计算，这里简化处理
        }

    def _calculate_wu_xing(self, chars: list) -> Dict:
        """计算五行分数"""
        scores = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}

        for char in chars:
            for element, chars_str in self.WU_XING.items():
                if char in chars_str:
                    scores[element] += 1
                    break

        return {"scores": scores, "description": self._format_wu_xing_desc(scores)}

    def _get_element(self, gan: str) -> str:
        """获取天干的五行属性"""
        for element, chars_str in self.WU_XING.items():
            if gan in chars_str:
                return element
        return "未知"

    def _format_wu_xing_desc(self, scores: Dict) -> str:
        """格式化五行描述"""
        parts = [f"{elem}{score}个" for elem, score in scores.items() if score > 0]
        return "、".join(parts)

    def _get_zhi_cang_gan(self, year_zhi, month_zhi, day_zhi, hour_zhi) -> Dict:
        """获取地支藏干"""
        return {
            "year": self.ZHI_CANG_GAN.get(year_zhi, []),
            "month": self.ZHI_CANG_GAN.get(month_zhi, []),
            "day": self.ZHI_CANG_GAN.get(day_zhi, []),
            "hour": self.ZHI_CANG_GAN.get(hour_zhi, []),
        }

    def _judge_balance(self, scores: Dict) -> str:
        """判断五行平衡"""
        values = list(scores.values())
        max_val = max(values)
        min_val = min(values)

        if max_val - min_val <= 1:
            return "五行平衡"
        elif max_val - min_val <= 3:
            return "五行较平衡"
        else:
            return "五行不平衡"

    def analyze_palace(
        self, birth_info: Dict[str, Any], palace_name: str, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        八字系统不支持宫位分析

        八字（四柱命理）没有宫位的概念，这是紫微斗数的特性

        Args:
            language: 输出语言（保留接口一致性）
        """
        raise NotImplementedError("八字系统不支持宫位分析，请使用紫微斗数系统")
