"""
命理系统实现模块
"""

from typing import Dict, Type

from core.base_system import BaseFortuneSystem
from core.exceptions import SystemNotFoundError

# 系统注册表
_SYSTEMS: Dict[str, Type[BaseFortuneSystem]] = {}

# 系统实例缓存
_SYSTEM_INSTANCES: Dict[str, BaseFortuneSystem] = {}


def register_system(name: str, system_class: Type[BaseFortuneSystem]):
    """
    注册命理系统

    Args:
        name: 系统名称（用于标识）
        system_class: 系统类
    """
    _SYSTEMS[name] = system_class


def get_system(name: str, cached: bool = True) -> BaseFortuneSystem:
    """
    获取命理系统实例（支持缓存）

    Args:
        name: 系统名称
        cached: 是否使用缓存实例，默认True

    Returns:
        系统实例

    Raises:
        SystemNotFoundError: 系统未注册

    Note:
        使用缓存可以提高性能，避免重复创建实例
        如果需要独立实例，可设置 cached=False
    """
    if name not in _SYSTEMS:
        raise SystemNotFoundError(
            f"System '{name}' not registered. Available: {list(_SYSTEMS.keys())}"
        )

    # 如果启用缓存且实例已存在，直接返回
    if cached and name in _SYSTEM_INSTANCES:
        return _SYSTEM_INSTANCES[name]

    # 创建新实例
    instance = _SYSTEMS[name]()

    # 如果启用缓存，保存实例
    if cached:
        _SYSTEM_INSTANCES[name] = instance

    return instance


def clear_cache(name: str = None):
    """
    清除系统实例缓存

    Args:
        name: 系统名称，如果为None则清除所有缓存
    """
    global _SYSTEM_INSTANCES

    if name is None:
        _SYSTEM_INSTANCES = {}
    elif name in _SYSTEM_INSTANCES:
        del _SYSTEM_INSTANCES[name]


def list_systems() -> list:
    """
    列出所有已注册的系统

    Returns:
        系统名称列表
    """
    return list(_SYSTEMS.keys())


# 自动导入并注册所有系统
try:
    from .ziwei import ZiweiSystem

    register_system("ziwei", ZiweiSystem)
except ImportError:
    pass

try:
    from .bazi import BaziSystem

    register_system("bazi", BaziSystem)
except ImportError:
    pass

try:
    from .astrology import AstrologySystem

    register_system("astrology", AstrologySystem)
except ImportError:
    pass


__all__ = ["register_system", "get_system", "clear_cache", "list_systems"]
