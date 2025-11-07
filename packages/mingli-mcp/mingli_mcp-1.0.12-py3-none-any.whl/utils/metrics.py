"""
性能监控指标收集器

提供请求性能统计、系统调用监控等功能
"""

from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Dict, List, Optional


@dataclass
class Metrics:
    """指标数据类"""

    # 请求统计
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0

    # 性能指标
    total_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    average_response_time: float = 0.0

    # 系统调用统计
    system_calls: Dict[str, int] = field(default_factory=dict)

    # 方法调用统计
    method_calls: Dict[str, int] = field(default_factory=dict)

    # 错误统计
    error_counts: Dict[str, int] = field(default_factory=dict)

    # 开始时间
    start_time: datetime = field(default_factory=datetime.now)

    # 线程锁
    _lock: Lock = field(default_factory=Lock, repr=False, compare=False)

    def record_request(
        self,
        system: str,
        method: str,
        duration: float,
        success: bool,
        error_type: Optional[str] = None,
    ):
        """
        记录请求

        Args:
            system: 系统名称（如 ziwei, bazi）
            method: 方法名称（如 get_chart, get_fortune）
            duration: 响应时间（秒）
            success: 是否成功
            error_type: 错误类型（如果失败）
        """
        with self._lock:
            # 更新请求计数
            self.total_requests += 1
            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1

            # 更新响应时间统计
            self.total_response_time += duration
            self.min_response_time = min(self.min_response_time, duration)
            self.max_response_time = max(self.max_response_time, duration)

            if self.total_requests > 0:
                self.average_response_time = self.total_response_time / self.total_requests

            # 更新系统调用统计
            self.system_calls[system] = self.system_calls.get(system, 0) + 1

            # 更新方法调用统计
            method_key = f"{system}.{method}"
            self.method_calls[method_key] = self.method_calls.get(method_key, 0) + 1

            # 更新错误统计
            if not success and error_type:
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

    def get_summary(self) -> Dict:
        """
        获取指标摘要

        Returns:
            指标摘要字典
        """
        with self._lock:
            uptime_seconds = (datetime.now() - self.start_time).total_seconds()

            return {
                "uptime_seconds": round(uptime_seconds, 2),
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "success_rate": (
                    round(self.successful_requests / self.total_requests * 100, 2)
                    if self.total_requests > 0
                    else 0.0
                ),
                "average_response_time": round(self.average_response_time, 3),
                "min_response_time": (
                    round(self.min_response_time, 3)
                    if self.min_response_time != float("inf")
                    else 0.0
                ),
                "max_response_time": round(self.max_response_time, 3),
                "requests_per_second": (
                    round(self.total_requests / uptime_seconds, 2) if uptime_seconds > 0 else 0.0
                ),
                "system_calls": dict(self.system_calls),
                "method_calls": dict(self.method_calls),
                "error_counts": dict(self.error_counts),
            }

    def get_top_methods(self, limit: int = 10) -> List[tuple]:
        """
        获取最常调用的方法

        Args:
            limit: 返回数量限制

        Returns:
            [(method, count), ...] 按调用次数降序排列
        """
        with self._lock:
            sorted_methods = sorted(self.method_calls.items(), key=lambda x: x[1], reverse=True)
            return sorted_methods[:limit]

    def get_top_errors(self, limit: int = 10) -> List[tuple]:
        """
        获取最常见的错误

        Args:
            limit: 返回数量限制

        Returns:
            [(error_type, count), ...] 按错误次数降序排列
        """
        with self._lock:
            sorted_errors = sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)
            return sorted_errors[:limit]

    def reset(self):
        """重置所有指标"""
        with self._lock:
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.total_response_time = 0.0
            self.min_response_time = float("inf")
            self.max_response_time = 0.0
            self.average_response_time = 0.0
            self.system_calls.clear()
            self.method_calls.clear()
            self.error_counts.clear()
            self.start_time = datetime.now()


# 全局指标收集器实例
_global_metrics = Metrics()


def get_metrics() -> Metrics:
    """
    获取全局指标收集器实例

    Returns:
        Metrics实例
    """
    return _global_metrics


def record_request(
    system: str,
    method: str,
    duration: float,
    success: bool,
    error_type: Optional[str] = None,
):
    """
    记录请求到全局指标收集器

    Args:
        system: 系统名称
        method: 方法名称
        duration: 响应时间（秒）
        success: 是否成功
        error_type: 错误类型（如果失败）
    """
    _global_metrics.record_request(system, method, duration, success, error_type)
