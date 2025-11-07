"""
HTTP传输层实现

基于FastAPI实现HTTP方式的MCP服务
适用于远程调用、云端部署等场景
"""

import logging
import secrets
from typing import Any, Callable, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import config
from utils.rate_limiter import RateLimiter

from .base_transport import BaseTransport

logger = logging.getLogger(__name__)


class HttpTransport(BaseTransport):
    """HTTP传输实现"""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8080,
        api_key: Optional[str] = None,
        enable_rate_limit: bool = True,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        cors_origins: Optional[List[str]] = None,
        cors_allow_credentials: bool = False,
    ):
        """
        初始化HTTP传输

        Args:
            host: 监听地址
            port: 监听端口
            api_key: API密钥（可选，用于认证）
            enable_rate_limit: 是否启用限流
            rate_limit_requests: 限流窗口内最大请求数
            rate_limit_window: 限流窗口大小（秒）
            cors_origins: 允许的CORS来源列表
            cors_allow_credentials: 是否允许携带凭证
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self.enable_rate_limit = enable_rate_limit

        # 初始化限流器
        if self.enable_rate_limit:
            self.rate_limiter = RateLimiter(
                max_requests=rate_limit_requests, window_seconds=rate_limit_window
            )
            logger.info(
                f"Rate limiter enabled: {rate_limit_requests} requests per {rate_limit_window}s"
            )

        self.app = FastAPI(
            title="Mingli MCP Server", description="命理MCP服务 - HTTP API", version="1.0.0"
        )

        # CORS配置 - 从配置文件读取或使用参数
        if cors_origins is None:
            cors_origins = config.CORS_ORIGINS.split(",")

        # 过滤空字符串
        cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

        # 如果没有配置，使用安全默认值
        if not cors_origins:
            cors_origins = ["http://localhost:3000", "http://localhost:8080"]
            logger.warning(
                "No CORS origins configured, using default: localhost only. "
                "Set CORS_ORIGINS environment variable for production."
            )

        # 添加CORS支持（安全配置）
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=cors_allow_credentials or config.CORS_ALLOW_CREDENTIALS,
            allow_methods=["GET", "POST", "OPTIONS"],  # 只允许必要的方法
            allow_headers=["Content-Type", "Authorization"],  # 只允许必要的头
        )

        logger.info(f"CORS enabled for origins: {cors_origins}")

        self._setup_routes()
        logger.info(f"HTTP transport initialized on {host}:{port}")

    def _setup_routes(self):
        """设置路由"""

        @self.app.get("/")
        async def root():
            """根路径"""
            return {
                "name": "Mingli MCP Server",
                "version": "1.0.0",
                "protocol": "MCP",
                "transport": "HTTP",
                "endpoints": {"mcp": "/mcp", "health": "/health", "docs": "/docs"},
            }

        @self.app.get("/health")
        async def health():
            """健康检查"""
            return {
                "status": "healthy",
                "transport": "http",
                "systems": ["ziwei", "bazi"],
                "rate_limiting": self.enable_rate_limit,
            }

        @self.app.get("/stats")
        async def stats(request: Request):
            """获取限流器统计信息（需要API key）"""
            # API密钥验证
            if self.api_key:
                auth_header = request.headers.get("Authorization", "")
                expected = f"Bearer {self.api_key}"
                # 使用常量时间比较防止时序攻击
                if not auth_header or not secrets.compare_digest(auth_header, expected):
                    logger.warning("Invalid API key attempt for /stats endpoint")
                    raise HTTPException(status_code=401, detail="Unauthorized")

            if not self.enable_rate_limit:
                return {"rate_limiting": False, "message": "Rate limiting is disabled"}

            return self.rate_limiter.get_stats()

        @self.app.post("/mcp")
        async def handle_mcp(request: Request):
            """处理MCP请求"""
            # 获取客户端标识（IP地址）
            client_id = request.client.host if request.client else "unknown"

            # 限流检查
            if self.enable_rate_limit and not self.rate_limiter.is_allowed(client_id):
                reset_time = self.rate_limiter.get_reset_time(client_id)
                reset_str = reset_time.isoformat() if reset_time else "unknown"

                logger.warning(f"Rate limit exceeded for client: {client_id}")

                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "message": "Rate limit exceeded. Please try again later.",
                        "reset_time": reset_str,
                    },
                    headers={
                        "X-RateLimit-Limit": str(self.rate_limiter.max_requests),
                        "X-RateLimit-Remaining": str(self.rate_limiter.get_remaining(client_id)),
                        "X-RateLimit-Reset": reset_str,
                    },
                )

            # API密钥验证（如果配置了）
            if self.api_key:
                auth_header = request.headers.get("Authorization", "")
                expected = f"Bearer {self.api_key}"
                # 使用常量时间比较防止时序攻击
                if not auth_header or not secrets.compare_digest(auth_header, expected):
                    logger.warning(f"Invalid API key attempt from {client_id}")
                    raise HTTPException(status_code=401, detail="Unauthorized")

            data = None
            try:
                # 获取请求数据
                data = await request.json()
                logger.debug(f"Received MCP request: {data.get('method')}")

                # 调用消息处理器
                if not self.message_handler:
                    raise HTTPException(status_code=500, detail="Message handler not set")

                response = self.message_handler(data)

                # 对于通知消息（无需响应），返回空
                if response is None:
                    return JSONResponse(content={}, status_code=204)

                return JSONResponse(content=response)

            except HTTPException:
                # FastAPI 异常直接抛出
                raise
            except Exception:
                # 记录完整错误详情到日志
                logger.exception("Error handling MCP request")
                # 返回通用错误消息，不暴露内部实现细节
                return JSONResponse(
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32603, "message": "Internal server error"},
                        "id": data.get("id") if data else None,
                    },
                    status_code=500,
                )

    def start(self):
        """启动HTTP服务器"""
        logger.info(f"Starting HTTP server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port, log_level="info")

    def stop(self):
        """停止HTTP服务器"""
        logger.info("HTTP server stopped")

    def send_message(self, message: Dict[str, Any]):
        """
        HTTP模式不需要主动发送消息
        响应由FastAPI自动处理
        """
        pass

    def receive_message(self) -> Optional[Dict[str, Any]]:
        """
        HTTP模式由FastAPI处理接收
        此方法不使用
        """
        pass

    def set_message_handler(self, handler: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """设置消息处理器"""
        self.message_handler = handler
        logger.debug("Message handler set for HTTP transport")
