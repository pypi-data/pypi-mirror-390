"""
请求限流器

实现基于滑动窗口的请求限流，防止API滥用
"""

import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Optional


class RateLimiter:
    """
    请求限流器

    使用滑动窗口算法限制请求频率
    """

    def __init__(
        self, max_requests: int = 100, window_seconds: int = 60, cleanup_interval: int = 300
    ):
        """
        初始化限流器

        Args:
            max_requests: 窗口期内最大请求数
            window_seconds: 时间窗口（秒）
            cleanup_interval: 清理过期数据的间隔（秒）
        """
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.cleanup_interval = cleanup_interval

        # 存储每个客户端的请求时间戳队列
        self.requests: Dict[str, deque] = defaultdict(deque)

        # 上次清理时间
        self.last_cleanup = time.time()

    def is_allowed(self, client_id: str) -> bool:
        """
        检查请求是否允许

        Args:
            client_id: 客户端标识（如IP地址、用户ID等）

        Returns:
            True表示允许请求，False表示超出限制
        """
        now = datetime.now()
        cutoff_time = now - self.window

        # 定期清理过期数据
        self._periodic_cleanup()

        # 清理该客户端的过期请求
        while self.requests[client_id] and self.requests[client_id][0] < cutoff_time:
            self.requests[client_id].popleft()

        # 检查是否超出限制
        if len(self.requests[client_id]) >= self.max_requests:
            return False

        # 记录本次请求
        self.requests[client_id].append(now)
        return True

    def get_remaining(self, client_id: str) -> int:
        """
        获取剩余可用请求数

        Args:
            client_id: 客户端标识

        Returns:
            剩余可用请求数
        """
        now = datetime.now()
        cutoff_time = now - self.window

        # 清理过期请求
        while self.requests[client_id] and self.requests[client_id][0] < cutoff_time:
            self.requests[client_id].popleft()

        used = len(self.requests[client_id])
        return max(0, self.max_requests - used)

    def get_reset_time(self, client_id: str) -> Optional[datetime]:
        """
        获取限流重置时间

        Args:
            client_id: 客户端标识

        Returns:
            重置时间，如果没有限流返回None
        """
        if not self.requests[client_id]:
            return None

        # 最早的请求时间 + 窗口时间 = 重置时间
        oldest_request = self.requests[client_id][0]
        return oldest_request + self.window

    def _periodic_cleanup(self):
        """定期清理所有客户端的过期请求"""
        now_time = time.time()

        # 如果距离上次清理超过cleanup_interval，执行清理
        if now_time - self.last_cleanup > self.cleanup_interval:
            now = datetime.now()
            cutoff_time = now - self.window

            # 清理所有客户端的过期请求
            clients_to_remove = []

            for client_id, request_queue in self.requests.items():
                # 清理过期请求
                while request_queue and request_queue[0] < cutoff_time:
                    request_queue.popleft()

                # 如果队列为空，标记删除
                if not request_queue:
                    clients_to_remove.append(client_id)

            # 删除空队列
            for client_id in clients_to_remove:
                del self.requests[client_id]

            self.last_cleanup = now_time

    def reset(self, client_id: str = None):
        """
        重置限流计数

        Args:
            client_id: 客户端标识，如果为None则重置所有客户端
        """
        if client_id is None:
            self.requests.clear()
        elif client_id in self.requests:
            del self.requests[client_id]

    def get_stats(self) -> Dict:
        """
        获取限流器统计信息

        Returns:
            统计信息字典
        """
        now = datetime.now()
        cutoff_time = now - self.window

        total_clients = len(self.requests)
        total_requests = 0
        limited_clients = 0

        for request_queue in self.requests.values():
            # 清理过期请求后计数
            active_requests = sum(1 for req_time in request_queue if req_time >= cutoff_time)
            total_requests += active_requests

            if active_requests >= self.max_requests:
                limited_clients += 1

        return {
            "total_clients": total_clients,
            "total_requests": total_requests,
            "limited_clients": limited_clients,
            "max_requests_per_window": self.max_requests,
            "window_seconds": self.window.total_seconds(),
        }
