"""
配置管理模块
"""

import logging
import os

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}

# 配置日志
# 在stdio模式下，日志必须输出到stderr或文件，不能干扰stdout
TRANSPORT_TYPE = os.getenv("TRANSPORT_TYPE", "stdio")

if TRANSPORT_TYPE == "stdio":
    # stdio模式：日志输出到stderr
    import sys

    logging.basicConfig(
        level=_LEVELS.get(LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],  # 明确输出到stderr
    )
else:
    # HTTP模式：可以输出到stdout
    logging.basicConfig(
        level=_LEVELS.get(LOG_LEVEL, logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


class Config:
    """配置类"""

    # MCP服务配置
    MCP_SERVER_NAME: str = os.getenv("MCP_SERVER_NAME", "ziwei_mcp")
    MCP_SERVER_VERSION: str = "1.0.11"

    # 默认语言
    DEFAULT_LANGUAGE: str = os.getenv("DEFAULT_LANGUAGE", "zh-CN")

    # 支持的语言列表
    SUPPORTED_LANGUAGES = [
        "zh-CN",  # 简体中文
        "zh-TW",  # 繁体中文
        "en-US",  # English
        "ja-JP",  # 日本語
        "ko-KR",  # 한국어
        "vi-VN",  # Tiếng Việt
    ]

    # 传输层配置
    TRANSPORT_TYPE: str = os.getenv("TRANSPORT_TYPE", "stdio")

    # HTTP传输配置
    HTTP_HOST: str = os.getenv("HTTP_HOST", "0.0.0.0")
    HTTP_PORT: int = int(os.getenv("HTTP_PORT", "8080"))
    HTTP_API_KEY: str = os.getenv("HTTP_API_KEY", "")

    # CORS配置（安全性）
    # 默认只允许本地访问，生产环境应明确指定允许的域名
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8080")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"

    # WebSocket传输配置（预留）
    WS_HOST: str = os.getenv("WS_HOST", "0.0.0.0")
    WS_PORT: int = int(os.getenv("WS_PORT", "8081"))

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """获取logger实例"""
        return logging.getLogger(name)


# 全局配置实例
config = Config()
