"""
八字系统格式化器

用于将八字数据格式化为JSON和Markdown格式
"""

from typing import Any, Dict


class BaziFormatter:
    """八字格式化器"""

    def format_chart(self, chart_data: Dict[str, Any], format_type: str = "json") -> str:
        """
        格式化八字排盘数据

        Args:
            chart_data: 排盘数据
            format_type: 格式类型 ('json' 或 'markdown')

        Returns:
            格式化后的字符串
        """
        if format_type == "markdown":
            return self._format_chart_markdown(chart_data)
        else:
            return chart_data

    def format_fortune(self, fortune_data: Dict[str, Any], format_type: str = "json") -> str:
        """
        格式化运势数据

        Args:
            fortune_data: 运势数据
            format_type: 格式类型

        Returns:
            格式化后的字符串
        """
        if format_type == "markdown":
            return self._format_fortune_markdown(fortune_data)
        else:
            return fortune_data

    def format_element_analysis(
        self, analysis_data: Dict[str, Any], format_type: str = "json"
    ) -> str:
        """
        格式化五行分析数据

        Args:
            analysis_data: 分析数据
            format_type: 格式类型

        Returns:
            格式化后的字符串
        """
        if format_type == "markdown":
            return self._format_element_markdown(analysis_data)
        else:
            return analysis_data

    def _format_chart_markdown(self, data: Dict[str, Any]) -> str:
        """格式化排盘为Markdown"""
        md = f"""# 八字排盘

## 基本信息
- **阳历**: {data['solar_date']}
- **农历**: {data['lunar_date']}
- **性别**: {data['gender']}
- **生肖**: {data['zodiac']}

## 四柱八字
```
{data['eight_char']}
```

### 详细四柱
| 柱 | 天干 | 地支 | 干支 |
|---|------|------|------|
| 年柱 | {data['pillars']['year']['gan']} | {data['pillars']['year']['zhi']} | {data['pillars']['year']['pillar']} |
| 月柱 | {data['pillars']['month']['gan']} | {data['pillars']['month']['zhi']} | {data['pillars']['month']['pillar']} |
| 日柱 | {data['pillars']['day']['gan']} | {data['pillars']['day']['zhi']} | {data['pillars']['day']['pillar']} |
| 时柱 | {data['pillars']['hour']['gan']} | {data['pillars']['hour']['zhi']} | {data['pillars']['hour']['pillar']} |

**日主**: {data['day_master']}（命主本身，以日干为准）

## 十神分析
- **年干**: {data['deities']['year_gan']}
- **月干**: {data['deities']['month_gan']}
- **日干**: {data['deities']['day_gan']}
- **时干**: {data['deities']['hour_gan']}

## 五行分析
- **分数**: {data['wu_xing']['description']}
- **详细**: 金{data['wu_xing']['scores']['金']} 木{data['wu_xing']['scores']['木']} 水{data['wu_xing']['scores']['水']} 火{data['wu_xing']['scores']['火']} 土{data['wu_xing']['scores']['土']}

## 地支藏干
- **年支** {data['pillars']['year']['zhi']}: {', '.join(data['zhi_cang_gan']['year'])}
- **月支** {data['pillars']['month']['zhi']}: {', '.join(data['zhi_cang_gan']['month'])}
- **日支** {data['pillars']['day']['zhi']}: {', '.join(data['zhi_cang_gan']['day'])}
- **时支** {data['pillars']['hour']['zhi']}: {', '.join(data['zhi_cang_gan']['hour'])}
"""
        return md

    def _format_fortune_markdown(self, data: Dict[str, Any]) -> str:
        """格式化运势为Markdown"""
        md = f"""# 八字运势

## 查询信息
- **查询日期**: {data['query_date']}
- **当前年龄**: {data['age']}岁
- **日主**: {data['day_master']}

## 大运
- **当前大运**: {data['da_yun']['description']}
- **年龄范围**: {data['da_yun']['age_range']}

## 流年
- **流年**: {data['liu_nian']['year']}年
- **干支**: {data['liu_nian']['gan_zhi']}
- **生肖**: {data['liu_nian']['zodiac']}

---

## 本命八字
```
{data['basic_chart']['eight_char']}
```
"""
        return md

    def _format_element_markdown(self, data: Dict[str, Any]) -> str:
        """格式化五行分析为Markdown"""
        md = f"""# 五行分析

## 日主信息
- **日主**: {data['day_master']}
- **五行**: {data['day_master_element']}

## 五行分数
| 五行 | 数量 | 百分比 |
|------|------|--------|
| 金 | {data['scores']['金']} | {data['percentages']['金']:.1f}% |
| 木 | {data['scores']['木']} | {data['percentages']['木']:.1f}% |
| 水 | {data['scores']['水']} | {data['percentages']['水']:.1f}% |
| 火 | {data['scores']['火']} | {data['percentages']['火']:.1f}% |
| 土 | {data['scores']['土']} | {data['percentages']['土']:.1f}% |

## 分析结果
- **最旺五行**: {data['strongest']['element']}（{data['strongest']['score']}个）
- **最弱五行**: {data['weakest']['element']}（{data['weakest']['score']}个）
- **缺失五行**: {', '.join(data['missing']) if data['missing'] else '无'}
- **平衡度**: {data['balance']}

## 建议
"""

        # 根据五行情况给出建议
        if data["missing"]:
            md += f"\n命局缺{', '.join(data['missing'])}，建议在生活中补充这些元素。\n"

        if data["balance"] == "五行不平衡":
            md += f"\n五行不够平衡，{data['strongest']['element']}过旺，{data['weakest']['element']}较弱，建议适当调和。\n"

        return md
