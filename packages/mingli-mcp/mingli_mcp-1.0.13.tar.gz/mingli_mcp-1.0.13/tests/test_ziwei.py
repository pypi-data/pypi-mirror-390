"""
紫微斗数系统测试
"""

import os
import sys
from datetime import datetime

from systems import get_system

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_ziwei_chart():
    """测试紫微排盘"""
    print("测试紫微排盘...")

    ziwei = get_system("ziwei")

    birth_info = {"date": "2000-08-16", "time_index": 2, "gender": "女", "calendar": "solar"}

    chart = ziwei.get_chart(birth_info)

    print(f"\n系统: {chart['system']}")
    print(f"阳历: {chart['basic_info']['阳历日期']}")
    print(f"农历: {chart['basic_info']['农历日期']}")
    print(f"命主: {chart['basic_info']['命主']}")
    print(f"宫位数量: {len(chart['palaces'])}")

    print("\n✅ 排盘测试通过")


def test_ziwei_fortune():
    """测试紫微运势"""
    print("\n测试紫微运势...")

    ziwei = get_system("ziwei")

    birth_info = {"date": "2000-08-16", "time_index": 2, "gender": "女", "calendar": "solar"}

    fortune = ziwei.get_fortune(birth_info, datetime.now())

    print(f"\n查询日期: {fortune['query_date']}")
    if "decadal" in fortune:
        print(f"大限: {fortune['decadal']['heavenly_stem']}{fortune['decadal']['earthly_branch']}")
    if "yearly" in fortune:
        print(f"流年: {fortune['yearly']['heavenly_stem']}{fortune['yearly']['earthly_branch']}")

    print("\n✅ 运势测试通过")


def test_ziwei_palace():
    """测试宫位分析"""
    print("\n测试宫位分析...")

    ziwei = get_system("ziwei")

    birth_info = {"date": "2000-08-16", "time_index": 2, "gender": "女", "calendar": "solar"}

    palace = ziwei.analyze_palace(birth_info, "命宫")

    print(f"\n宫位: {palace['palace_name']}")
    print(f"天干地支: {palace['heavenly_stem']}{palace['earthly_branch']}")
    print(f"主星数量: {len(palace.get('major_stars', []))}")

    print("\n✅ 宫位分析测试通过")


def test_lunar_calendar():
    """测试农历输入"""
    print("\n测试农历输入...")

    ziwei = get_system("ziwei")

    birth_info = {
        "date": "2000-07-17",  # 农历
        "time_index": 2,
        "gender": "女",
        "calendar": "lunar",
    }

    chart = ziwei.get_chart(birth_info)

    print(f"\n农历: {chart['basic_info']['农历日期']}")
    print(f"阳历: {chart['basic_info']['阳历日期']}")

    print("\n✅ 农历测试通过")


if __name__ == "__main__":
    try:
        test_ziwei_chart()
        test_ziwei_fortune()
        test_ziwei_palace()
        test_lunar_calendar()

        print("\n" + "=" * 50)
        print("🎉 所有测试通过！")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()
