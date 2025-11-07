#!/usr/bin/env python3
"""
八字系统测试

测试八字排盘、运势、五行分析功能
"""

import sys
from datetime import datetime
from pathlib import Path

from systems import get_system

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_bazi_chart():
    """测试八字排盘"""
    print("\n" + "=" * 60)
    print("测试八字排盘")
    print("=" * 60)

    birth_info = {
        "date": "2000-08-16",
        "time_index": 2,  # 寅时
        "gender": "女",
        "calendar": "solar",
    }

    system = get_system("bazi")
    chart = system.get_chart(birth_info)

    # 验证关键字段
    assert "solar_date" in chart
    assert "lunar_date" in chart
    assert "gender" in chart
    assert chart["gender"] == "女"
    assert "zodiac" in chart
    assert "eight_char" in chart
    assert "day_master" in chart
    assert "pillars" in chart
    assert "deities" in chart
    assert "wu_xing" in chart

    print(f"\n阳历: {chart['solar_date']}")
    print(f"农历: {chart['lunar_date']}")
    print(f"性别: {chart['gender']}")
    print(f"生肖: {chart['zodiac']}")
    print(f"\n八字: {chart['eight_char']}")
    print(f"日主: {chart['day_master']}")

    print("\n四柱详情:")
    for pillar_name, pillar_data in chart["pillars"].items():
        print(
            f"  {pillar_name}柱: {pillar_data['pillar']} (干:{pillar_data['gan']} 支:{pillar_data['zhi']})"
        )

    print("\n十神:")
    for pos, deity in chart["deities"].items():
        print(f"  {pos}: {deity}")

    print("\n五行分数:")
    for element, score in chart["wu_xing"]["scores"].items():
        print(f"  {element}: {score}")

    print("\n✅ 排盘测试通过")


def test_bazi_fortune():
    """测试八字运势"""
    print("\n" + "=" * 60)
    print("测试八字运势")
    print("=" * 60)

    birth_info = {"date": "2000-08-16", "time_index": 2, "gender": "女", "calendar": "solar"}

    system = get_system("bazi")
    fortune = system.get_fortune(birth_info, datetime.now())

    # 验证关键字段
    assert "query_date" in fortune
    assert "age" in fortune
    assert fortune["age"] > 0
    assert "day_master" in fortune
    assert "da_yun" in fortune
    assert "liu_nian" in fortune

    print(f"\n查询日期: {fortune['query_date']}")
    print(f"当前年龄: {fortune['age']}岁")
    print(f"日主: {fortune['day_master']}")

    print("\n大运:")
    print(f"  {fortune['da_yun']['description']}")
    print(f"  年龄范围: {fortune['da_yun']['age_range']}")

    print("\n流年:")
    print(f"  {fortune['liu_nian']['year']}年")
    print(f"  干支: {fortune['liu_nian']['gan_zhi']}")
    print(f"  生肖: {fortune['liu_nian']['zodiac']}")

    print("\n✅ 运势测试通过")


def test_element_analysis():
    """测试五行分析"""
    print("\n" + "=" * 60)
    print("测试五行分析")
    print("=" * 60)

    birth_info = {"date": "2000-08-16", "time_index": 2, "gender": "女", "calendar": "solar"}

    system = get_system("bazi")
    analysis = system.analyze_element(birth_info)

    # 验证关键字段
    assert "day_master" in analysis
    assert "day_master_element" in analysis
    assert "scores" in analysis
    assert "percentages" in analysis
    assert "strongest" in analysis
    assert "weakest" in analysis
    assert "missing" in analysis
    assert "balance" in analysis

    print(f"\n日主: {analysis['day_master']} ({analysis['day_master_element']})")

    print("\n五行分数:")
    for element, score in analysis["scores"].items():
        percentage = analysis["percentages"][element]
        print(f"  {element}: {score}个 ({percentage:.1f}%)")

    print(f"\n最旺五行: {analysis['strongest']['element']} ({analysis['strongest']['score']}个)")
    print(f"最弱五行: {analysis['weakest']['element']} ({analysis['weakest']['score']}个)")

    if analysis["missing"]:
        print(f"缺失五行: {', '.join(analysis['missing'])}")
    else:
        print("缺失五行: 无")

    print(f"平衡度: {analysis['balance']}")

    print("\n✅ 五行分析测试通过")


def test_lunar_calendar():
    """测试农历输入"""
    print("\n" + "=" * 60)
    print("测试农历输入")
    print("=" * 60)

    birth_info = {
        "date": "2000-07-17",  # 农历
        "time_index": 2,
        "gender": "女",
        "calendar": "lunar",
    }

    system = get_system("bazi")
    chart = system.get_chart(birth_info)

    # 验证关键字段
    assert "lunar_date" in chart
    assert "solar_date" in chart
    assert "eight_char" in chart

    print(f"\n农历: {chart['lunar_date']}")
    print(f"阳历: {chart['solar_date']}")
    print(f"八字: {chart['eight_char']}")

    print("\n✅ 农历测试通过")


def main():
    """运行所有测试"""
    print("\n" + "🔮" * 20)
    print("八字系统测试")
    print("🔮" * 20)

    tests = [
        test_bazi_chart,
        test_bazi_fortune,
        test_element_analysis,
        test_lunar_calendar,
    ]

    results = []
    for test_func in tests:
        results.append(test_func())

    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"\n通过: {passed}/{total}")

    if all(results):
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n⚠️  部分测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
