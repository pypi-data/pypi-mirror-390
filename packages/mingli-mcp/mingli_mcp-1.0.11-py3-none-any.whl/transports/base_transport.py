"""
传输层抽象基类

定义MCP传输层的统一接口，支持不同传输方式
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class BaseTransport(ABC):
    """传输层抽象基类"""

    def __init__(self):
        self.message_handler: Optional[Callable] = None
        self.running = False

    def set_message_handler(self, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """
        设置消息处理器

        Args:
            handler: 消息处理函数，接收请求字典，返回响应字典
        """
        self.message_handler = handler

    @abstractmethod
    def start(self) -> None:
        """
        启动传输层

        开始监听和处理消息
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        停止传输层

        清理资源并停止监听
        """
        pass

    @abstractmethod
    def send_message(self, message: Dict[str, Any]) -> None:
        """
        发送消息

        Args:
            message: 要发送的消息字典
        """
        pass

    @abstractmethod
    def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        接收消息

        Returns:
            接收到的消息字典，如果没有消息返回None
        """
        pass

    def get_transport_name(self) -> str:
        """
        返回传输层名称

        Returns:
            传输层名称，如 "stdio"、"http"、"websocket"
        """
        return self.__class__.__name__.replace("Transport", "").lower()

    def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理接收到的消息

        Args:
            message: 接收到的消息

        Returns:
            处理结果消息
        """
        if self.message_handler is None:
            logger.error("Message handler not set")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error: message handler not configured",
                },
                "id": message.get("id"),
            }

        try:
            return self.message_handler(message)
        except Exception as e:
            logger.exception("Error handling message")
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
                "id": message.get("id"),
            }
