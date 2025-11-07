"""
MCP传输层抽象模块

支持多种传输方式：
- stdio: 标准输入输出（默认，用于Cursor等IDE）
- http: HTTP/HTTPS传输（用于Web服务）
- websocket: WebSocket传输（用于实时应用）
"""

from .base_transport import BaseTransport
from .stdio_transport import StdioTransport

# 延迟导入 HTTP 传输（需要 uvicorn 依赖）
try:
    from .http_transport import HttpTransport

    HTTP_TRANSPORT_AVAILABLE = True
except ImportError:
    HttpTransport = None
    HTTP_TRANSPORT_AVAILABLE = False

__all__ = ["BaseTransport", "StdioTransport", "HttpTransport", "HTTP_TRANSPORT_AVAILABLE"]
