#!/usr/bin/env python3
"""
命理MCP服务器主入口

支持多种命理系统（紫微斗数、八字、占星等）的MCP集成
支持多种传输方式（stdio、HTTP、WebSocket）
"""

import sys
from datetime import datetime
from typing import Any, Dict

from config import config
from core.exceptions import (
    SystemError,
    SystemNotFoundError,
    ToolCallError,
    ValidationError,
)
from systems import get_system, list_systems
from systems.bazi.formatter import BaziFormatter
from systems.ziwei.formatter import ZiweiFormatter
from transports import StdioTransport
from utils.formatters import format_error_response, format_success_response

logger = config.get_logger(__name__)


class MingliMCPServer:
    """命理MCP服务器"""

    # MCP协议版本
    PROTOCOL_VERSION = "2024-11-05"

    def __init__(self):
        self.transport = None
        self.ziwei_formatter = ZiweiFormatter()
        self.bazi_formatter = BaziFormatter()
        self._initialize_transport()

    def _initialize_transport(self):
        """初始化传输层"""
        from transports import HTTP_TRANSPORT_AVAILABLE

        transport_type = config.TRANSPORT_TYPE.lower()

        if transport_type == "stdio":
            self.transport = StdioTransport()
        elif transport_type == "http":
            if not HTTP_TRANSPORT_AVAILABLE:
                raise ImportError(
                    "HTTP transport is not available. Please install mingli-mcp with HTTP support:\n"
                    "  pip install mingli-mcp[http]\n"
                    "or\n"
                    "  pip install mingli-mcp (which includes all dependencies)"
                )
            from transports import HttpTransport

            self.transport = HttpTransport(
                host=config.HTTP_HOST, port=config.HTTP_PORT, api_key=config.HTTP_API_KEY
            )
        # 预留WebSocket传输方式
        # elif transport_type == 'websocket':
        #     self.transport = WebSocketTransport(config.WS_HOST, config.WS_PORT)
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

        self.transport.set_message_handler(self.handle_request)
        logger.info(f"Initialized {transport_type} transport")

    def start(self):
        """启动MCP服务器"""
        logger.info(f"Starting {config.MCP_SERVER_NAME} v{config.MCP_SERVER_VERSION}")
        logger.info(f"Available systems: {', '.join(list_systems())}")
        self.transport.start()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理MCP请求

        Args:
            request: JSON-RPC请求

        Returns:
            JSON-RPC响应
        """
        method = request.get("method")
        request_id = request.get("id")

        try:
            # 初始化请求
            if method == "initialize":
                return self._handle_initialize(request, request_id)

            # 通知消息（无需响应）
            elif method == "notifications/initialized":
                logger.info("Received initialized notification")
                return None

            # 列出工具
            elif method == "tools/list":
                return self._handle_tools_list(request_id)

            # 调用工具
            elif method == "tools/call":
                return self._handle_tools_call(request, request_id)

            # 列出提示词
            elif method == "prompts/list":
                return self._handle_prompts_list(request_id)

            # 获取提示词
            elif method == "prompts/get":
                return self._handle_prompts_get(request, request_id)

            # 列出资源
            elif method == "resources/list":
                return self._handle_resources_list(request_id)

            # 获取资源
            elif method == "resources/get":
                return self._handle_resources_get(request, request_id)

            # 未知方法
            else:
                logger.warning(f"Unknown method: {method}")
                return format_error_response(-32601, f"Method not found: {method}", request_id)

        except (ValidationError, SystemNotFoundError) as e:
            logger.error(f"Request validation error for {method}: {e}")
            return format_error_response(-32602, str(e), request_id)
        except Exception as e:
            logger.exception(f"Unexpected error handling request: {method}")
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)

    def _handle_initialize(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理初始化请求"""
        client_info = request.get("params", {})
        logger.info(f"Client info: {client_info}")

        return format_success_response(
            {
                "protocolVersion": self.PROTOCOL_VERSION,
                "serverInfo": {
                    "name": config.MCP_SERVER_NAME,
                    "version": config.MCP_SERVER_VERSION,
                },
                "capabilities": {
                    "tools": {},
                    "prompts": {},
                    "resources": {},
                },
                # 真正的零配置体验 - 所有配置通过环境变量和合理默认值处理
                # 移除 configSchema 以符合 MCP 最佳实践（无需配置即可运行）
                "instructions": "命理MCP服务提供紫微斗数、八字等中国传统命理系统的分析工具。所有配置都是可选的，服务器可以在没有任何配置的情况下运行。可通过环境变量自定义行为（LOG_LEVEL, TRANSPORT_TYPE, DEFAULT_LANGUAGE等），详见文档。",
            },
            request_id,
        )

    def _handle_tools_list(self, request_id: Any) -> Dict[str, Any]:
        """处理工具列表请求"""
        tools = [
            {
                "name": "get_ziwei_chart",
                "description": "获取紫微斗数排盘信息，包含命盘十二宫、主星、辅星、四化等详细信息",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                        },
                        "time_index": {
                            "type": "integer",
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
                            "minimum": 0,
                            "maximum": 12,
                        },
                        "gender": {
                            "type": "string",
                            "enum": ["男", "女"],
                            "description": "性别：男 或 女",
                        },
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                            "default": "zh-CN",
                            "description": "输出语言：zh-CN(简体中文)、zh-TW(繁体中文)、en-US(English)、ja-JP(日本語)、ko-KR(한국어)、vi-VN(Tiếng Việt)，默认为zh-CN",
                        },
                    },
                    "required": ["date", "time_index", "gender"],
                },
            },
            {
                "name": "get_ziwei_fortune",
                "description": "获取紫微斗数运势信息，包含大限、流年、流月、流日、流时的运势详情",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "birth_date": {
                            "type": "string",
                            "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                        },
                        "time_index": {
                            "type": "integer",
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
                            "minimum": 0,
                            "maximum": 12,
                        },
                        "gender": {
                            "type": "string",
                            "enum": ["男", "女"],
                            "description": "性别：男 或 女",
                        },
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "query_date": {
                            "type": "string",
                            "description": "查询运势的日期，格式：YYYY-MM-DD，例如：2025-01-15。不填则为今天",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                            "default": "zh-CN",
                            "description": "输出语言：zh-CN(简体中文)、zh-TW(繁体中文)、en-US(English)、ja-JP(日本語)、ko-KR(한국어)、vi-VN(Tiếng Việt)，默认为zh-CN",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender"],
                },
            },
            {
                "name": "analyze_ziwei_palace",
                "description": "分析紫微斗数特定宫位的详细信息，包括该宫位的星曜配置、大限、四化等",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "birth_date": {
                            "type": "string",
                            "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                        },
                        "time_index": {
                            "type": "integer",
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
                            "minimum": 0,
                            "maximum": 12,
                        },
                        "gender": {
                            "type": "string",
                            "enum": ["男", "女"],
                            "description": "性别：男 或 女",
                        },
                        "palace_name": {
                            "type": "string",
                            "enum": [
                                "命宫",
                                "兄弟",
                                "夫妻",
                                "子女",
                                "财帛",
                                "疾厄",
                                "迁移",
                                "仆役",
                                "官禄",
                                "田宅",
                                "福德",
                                "父母",
                            ],
                            "description": "要分析的宫位名称。可选值：命宫(命运)、兄弟(兄弟姐妹)、夫妻(婚姻)、子女(子女)、财帛(财富)、疾厄(健康)、迁移(外出)、仆役(朋友)、官禄(事业)、田宅(房产)、福德(福气)、父母(父母)",
                        },
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                            "default": "zh-CN",
                            "description": "输出语言：zh-CN(简体中文)、zh-TW(繁体中文)、en-US(English)、ja-JP(日本語)、ko-KR(한국어)、vi-VN(Tiếng Việt)，默认为zh-CN",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender", "palace_name"],
                },
            },
            {
                "name": "list_fortune_systems",
                "description": "列出所有可用的命理系统（紫微斗数、八字、占星等）",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "description": "可选参数：detailed 为 true 时输出更详细信息（默认 false）",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "是否输出更详细信息（默认 false）",
                            "default": False,
                        }
                    },
                    "required": [],
                    "additionalProperties": False,
                },
            },
            {
                "name": "get_bazi_chart",
                "description": "获取八字（四柱）排盘信息，包含年月日时四柱、十神、五行、地支藏干等详细信息",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                        },
                        "time_index": {
                            "type": "integer",
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
                            "minimum": 0,
                            "maximum": 12,
                        },
                        "gender": {
                            "type": "string",
                            "enum": ["男", "女"],
                            "description": "性别：男 或 女",
                        },
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                            "default": "zh-CN",
                            "description": "输出语言：zh-CN(简体中文)、zh-TW(繁体中文)、en-US(English)、ja-JP(日本語)、ko-KR(한국어)、vi-VN(Tiếng Việt)，默认为zh-CN (八字暂不支持多语言，保留此参数以保持接口一致性)",
                        },
                    },
                    "required": ["date", "time_index", "gender"],
                },
            },
            {
                "name": "get_bazi_fortune",
                "description": "获取八字运势信息，包含大运、流年等详情",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "birth_date": {
                            "type": "string",
                            "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                        },
                        "time_index": {
                            "type": "integer",
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
                            "minimum": 0,
                            "maximum": 12,
                        },
                        "gender": {
                            "type": "string",
                            "enum": ["男", "女"],
                            "description": "性别：男 或 女",
                        },
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "query_date": {
                            "type": "string",
                            "description": "查询运势的日期，格式：YYYY-MM-DD，例如：2025-01-15。不填则为今天",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                            "default": "zh-CN",
                            "description": "输出语言：zh-CN(简体中文)、zh-TW(繁体中文)、en-US(English)、ja-JP(日本語)、ko-KR(한국어)、vi-VN(Tiếng Việt)，默认为zh-CN (八字暂不支持多语言，保留此参数以保持接口一致性)",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender"],
                },
            },
            {
                "name": "analyze_bazi_element",
                "description": "分析八字五行强弱，包含五行分数、平衡度、缺失五行等",
                "annotations": {
                    "readOnlyHint": True,
                    "destructiveHint": False,
                    "idempotentHint": True,
                },
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "birth_date": {
                            "type": "string",
                            "description": "出生日期，格式：YYYY-MM-DD，例如：2000-08-16",
                        },
                        "time_index": {
                            "type": "integer",
                            "description": "出生时辰序号（0-12）：0=早子时(23-01), 1=丑时(01-03), 2=寅时(03-05), 3=卯时(05-07), 4=辰时(07-09), 5=巳时(09-11), 6=午时(11-13), 7=未时(13-15), 8=申时(15-17), 9=酉时(17-19), 10=戌时(19-21), 11=亥时(21-23), 12=晚子时(23-01)",
                            "minimum": 0,
                            "maximum": 12,
                        },
                        "gender": {
                            "type": "string",
                            "enum": ["男", "女"],
                            "description": "性别：男 或 女",
                        },
                        "calendar": {
                            "type": "string",
                            "enum": ["solar", "lunar"],
                            "default": "solar",
                            "description": "历法类型：solar(阳历/公历) 或 lunar(农历/阴历)，默认为阳历",
                        },
                        "is_leap_month": {
                            "type": "boolean",
                            "default": False,
                            "description": "是否为闰月（仅当calendar=lunar时有效），默认为否",
                        },
                        "format": {
                            "type": "string",
                            "enum": ["json", "markdown"],
                            "default": "markdown",
                            "description": "输出格式：json(结构化数据) 或 markdown(易读格式)，默认为markdown",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["zh-CN", "zh-TW", "en-US", "ja-JP", "ko-KR", "vi-VN"],
                            "default": "zh-CN",
                            "description": "输出语言：zh-CN(简体中文)、zh-TW(繁体中文)、en-US(English)、ja-JP(日本語)、ko-KR(한국어)、vi-VN(Tiếng Việt)，默认为zh-CN (八字暂不支持多语言，保留此参数以保持接口一致性)",
                        },
                    },
                    "required": ["birth_date", "time_index", "gender"],
                },
            },
        ]

        return format_success_response({"tools": tools}, request_id)

    def _handle_tools_call(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理工具调用请求"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        logger.info(f"Tool call: {tool_name}")
        logger.debug(f"Arguments: {arguments}")

        try:
            # 紫微斗数排盘
            if tool_name == "get_ziwei_chart":
                result = self._tool_get_ziwei_chart(arguments)

            # 紫微斗数运势
            elif tool_name == "get_ziwei_fortune":
                result = self._tool_get_ziwei_fortune(arguments)

            # 紫微宫位分析
            elif tool_name == "analyze_ziwei_palace":
                result = self._tool_analyze_ziwei_palace(arguments)

            # 列出系统
            elif tool_name == "list_fortune_systems":
                result = self._tool_list_systems(arguments)

            # 八字排盘
            elif tool_name == "get_bazi_chart":
                result = self._tool_get_bazi_chart(arguments)

            # 八字运势
            elif tool_name == "get_bazi_fortune":
                result = self._tool_get_bazi_fortune(arguments)

            # 八字五行分析
            elif tool_name == "analyze_bazi_element":
                result = self._tool_analyze_bazi_element(arguments)

            else:
                return format_error_response(-32602, f"Unknown tool: {tool_name}", request_id)

            return format_success_response(
                {"content": [{"type": "text", "text": result}]}, request_id
            )

        except ValidationError as e:
            logger.error(f"Parameter validation error: {e}")
            return format_error_response(-32602, str(e), request_id)

        except SystemNotFoundError as e:
            logger.error(f"System not found: {e}")
            return format_error_response(-32602, str(e), request_id)

        except SystemError as e:
            logger.error(f"System execution error: {e}")
            return format_error_response(-32603, str(e), request_id)

        except ToolCallError as e:
            logger.error(f"Tool call error: {e}")
            return format_error_response(-32603, str(e), request_id)

        except Exception as e:
            logger.exception("Unexpected error in tool call")
            return format_error_response(-32603, f"Internal error: {str(e)}", request_id)

    def _tool_get_ziwei_chart(self, args: Dict[str, Any]) -> str:
        """工具：获取紫微斗数排盘"""
        birth_info = {
            "date": args["date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        language = args.get("language", "zh-CN")
        system = get_system("ziwei")
        chart = system.get_chart(birth_info, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(chart, ensure_ascii=False, indent=2)
        else:
            return self.ziwei_formatter.format_chart_markdown(chart)

    def _tool_get_ziwei_fortune(self, args: Dict[str, Any]) -> str:
        """工具：获取紫微斗数运势"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        # 解析查询日期
        query_date_str = args.get("query_date")
        if query_date_str:
            query_date = datetime.strptime(query_date_str, "%Y-%m-%d")
        else:
            query_date = datetime.now()

        language = args.get("language", "zh-CN")
        system = get_system("ziwei")
        fortune = system.get_fortune(birth_info, query_date, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(fortune, ensure_ascii=False, indent=2)
        else:
            return self.ziwei_formatter.format_fortune_markdown(fortune)

    def _tool_analyze_ziwei_palace(self, args: Dict[str, Any]) -> str:
        """工具：分析紫微斗数宫位"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        palace_name = args["palace_name"]
        language = args.get("language", "zh-CN")

        system = get_system("ziwei")
        analysis = system.analyze_palace(birth_info, palace_name, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(analysis, ensure_ascii=False, indent=2)
        else:
            return self.ziwei_formatter.format_palace_analysis_markdown(analysis)

    def _tool_list_systems(self, args: Dict[str, Any]) -> str:
        """工具：列出所有命理系统

        可选参数：
        - detailed: 是否输出更详细的信息（默认False）
        """
        systems = list_systems()

        detailed = bool(args.get("detailed", False))

        result = "# 可用的命理系统\n\n"
        for system_name in systems:
            try:
                system = get_system(system_name)
                capabilities = system.get_capabilities()

                result += f"## {system.get_system_name()}\n\n"
                result += f"- **版本**: {system.get_system_version()}\n"
                result += f"- **系统ID**: {system_name}\n"
                result += "- **功能支持**:\n"
                for cap_name, cap_value in capabilities.items():
                    status = "✅" if cap_value else "❌"
                    result += f"  - {cap_name}: {status}\n"

                if detailed and hasattr(system, "get_supported_palaces"):
                    palaces = system.get_supported_palaces()
                    if palaces:
                        result += f"- **支持宫位**: {', '.join(palaces)}\n"

                result += "\n"
            except Exception as e:
                result += f"## {system_name}\n\n"
                result += f"- **状态**: 加载失败 - {str(e)}\n\n"

        return result

    def _tool_get_bazi_chart(self, args: Dict[str, Any]) -> str:
        """工具：获取八字排盘"""
        birth_info = {
            "date": args["date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        language = args.get("language", "zh-CN")
        system = get_system("bazi")
        chart = system.get_chart(birth_info, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(chart, ensure_ascii=False, indent=2)
        else:
            return self.bazi_formatter.format_chart(chart, "markdown")

    def _tool_get_bazi_fortune(self, args: Dict[str, Any]) -> str:
        """工具：获取八字运势"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        # 解析查询日期
        query_date_str = args.get("query_date")
        if query_date_str:
            query_date = datetime.strptime(query_date_str, "%Y-%m-%d")
        else:
            query_date = datetime.now()

        language = args.get("language", "zh-CN")
        system = get_system("bazi")
        fortune = system.get_fortune(birth_info, query_date, language)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(fortune, ensure_ascii=False, indent=2)
        else:
            return self.bazi_formatter.format_fortune(fortune, "markdown")

    def _tool_analyze_bazi_element(self, args: Dict[str, Any]) -> str:
        """工具：分析八字五行"""
        birth_info = {
            "date": args["birth_date"],
            "time_index": args["time_index"],
            "gender": args["gender"],
            "calendar": args.get("calendar", "solar"),
            "is_leap_month": args.get("is_leap_month", False),
        }

        system = get_system("bazi")
        analysis = system.analyze_element(birth_info)

        output_format = args.get("format", "markdown")
        if output_format == "json":
            import json

            return json.dumps(analysis, ensure_ascii=False, indent=2)
        else:
            return self.bazi_formatter.format_element_analysis(analysis, "markdown")

    def _handle_prompts_list(self, request_id: Any) -> Dict[str, Any]:
        """处理提示词列表请求"""
        import os

        prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        prompts = []

        if os.path.exists(prompts_dir):
            for filename in os.listdir(prompts_dir):
                if filename.endswith(".md"):
                    filepath = os.path.join(prompts_dir, filename)
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Extract title from first line
                        lines = content.split("\n")
                        title = lines[0].replace("#", "").strip()
                        description = ""
                        # Find description section or use first paragraph
                        for line in lines[1:]:
                            if line.strip() and not line.startswith("#"):
                                description = line.strip()
                                break

                        prompt_name = filename[:-3]  # Remove .md extension
                        prompts.append(
                            {
                                "name": prompt_name,
                                "description": description or title,
                            }
                        )

        return format_success_response({"prompts": prompts}, request_id)

    def _handle_prompts_get(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理获取提示词请求"""
        from pathlib import Path

        params = request.get("params", {})
        name = params.get("name")
        arguments = params.get("arguments", {})

        if not name:
            return format_error_response(-32602, "Prompt name is required", request_id)

        # 安全性：验证文件名，防止路径遍历攻击
        if "/" in name or "\\" in name or name.startswith(".") or ".." in name:
            logger.warning(f"Potential path traversal attempt: {name}")
            return format_error_response(-32602, "Invalid prompt name", request_id)

        prompts_dir = Path(__file__).parent / "prompts"
        filepath = prompts_dir / f"{name}.md"

        # 确保目标文件在 prompts 目录内
        try:
            filepath.resolve().relative_to(prompts_dir.resolve())
        except ValueError:
            logger.warning(f"Path traversal blocked: {filepath}")
            return format_error_response(-32602, "Invalid prompt path", request_id)

        if not filepath.exists():
            return format_error_response(-32602, f"Prompt not found: {name}", request_id)

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Format the prompt with any arguments
        try:
            formatted_content = content.format(**arguments)
        except (KeyError, ValueError):
            formatted_content = content

        return format_success_response(
            {
                "description": "命理咨询提示词模板",
                "messages": [
                    {
                        "role": "user",
                        "content": {"type": "text", "text": formatted_content},
                    }
                ],
            },
            request_id,
        )

    def _handle_resources_list(self, request_id: Any) -> Dict[str, Any]:
        """处理资源列表请求"""
        resources = [
            {
                "uri": "mingli://configuration",
                "name": "服务器配置选项",
                "description": "可选的环境变量配置，用于自定义服务器行为（无配置也可正常运行）",
            },
            {
                "uri": "mingli://heavenly-stems",
                "name": "天干地支对照表",
                "description": "十天干十二地支的详细信息，包括五行属性、阴阳属性等",
            },
            {
                "uri": "mingli://five-elements",
                "name": "五行相生相克",
                "description": "五行（金木水火土）的相生相克关系和特性",
            },
            {
                "uri": "mingli://twelve-palaces",
                "name": "紫微十二宫位",
                "description": "紫微斗数十二宫位的名称、含义和主事",
            },
            {
                "uri": "mingli://ziwei-main-stars",
                "name": "紫微主星",
                "description": "紫微斗数十四主星的特性和影响",
            },
            {
                "uri": "mingli://time-periods",
                "name": "十二时辰对照表",
                "description": "十二时辰与现代表时间的对照关系",
            },
            {
                "uri": "mingli://fortune-terms",
                "name": "命理术语表",
                "description": "常用的命理术语及其含义解释",
            },
        ]

        return format_success_response({"resources": resources}, request_id)

    def _handle_resources_get(self, request: Dict[str, Any], request_id: Any) -> Dict[str, Any]:
        """处理获取资源请求"""
        params = request.get("params", {})
        uri = params.get("uri")

        if not uri:
            return format_error_response(-32602, "Resource URI is required", request_id)

        # Get resource content based on URI
        if uri == "mingli://configuration":
            content = self._get_configuration_content()
        elif uri == "mingli://heavenly-stems":
            content = self._get_heavenly_stems_content()
        elif uri == "mingli://five-elements":
            content = self._get_five_elements_content()
        elif uri == "mingli://twelve-palaces":
            content = self._get_twelve_palaces_content()
        elif uri == "mingli://ziwei-main-stars":
            content = self._get_ziwei_main_stars_content()
        elif uri == "mingli://time-periods":
            content = self._get_time_periods_content()
        elif uri == "mingli://fortune-terms":
            content = self._get_fortune_terms_content()
        else:
            return format_error_response(-32602, f"Resource not found: {uri}", request_id)

        return format_success_response(
            {
                "contents": [
                    {
                        "type": "text",
                        "text": content,
                    }
                ]
            },
            request_id,
        )

    def _get_configuration_content(self) -> str:
        """获取配置选项内容"""
        return """# 服务器配置选项

## 重要说明

**本服务器无需任何配置即可运行**。所有配置选项都是可选的，用于自定义服务器行为。

## 可选环境变量

### LOG_LEVEL
- **描述**: 日志级别
- **可选值**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **默认值**: INFO
- **示例**: `LOG_LEVEL=DEBUG`

### TRANSPORT_TYPE
- **描述**: 传输协议类型
- **可选值**: stdio, http
- **默认值**: stdio
- **示例**: `TRANSPORT_TYPE=stdio`
- **说明**: stdio模式用于MCP客户端集成，http模式用于Docker部署

### HTTP_HOST
- **描述**: HTTP服务器监听地址（仅HTTP模式）
- **默认值**: 0.0.0.0
- **示例**: `HTTP_HOST=localhost`

### HTTP_PORT
- **描述**: HTTP服务器端口（仅HTTP模式）
- **默认值**: 8080
- **示例**: `HTTP_PORT=3000`

### HTTP_API_KEY
- **描述**: HTTP API密钥（仅HTTP模式，可选）
- **默认值**: ""（空字符串，不启用认证）
- **示例**: `HTTP_API_KEY=your-secret-key`

### DEFAULT_LANGUAGE
- **描述**: 默认语言
- **默认值**: zh-CN
- **示例**: `DEFAULT_LANGUAGE=zh-CN`

## 使用示例

### Claude Desktop配置（无需配置）
```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"]
    }
  }
}
```

### 自定义日志级别
```json
{
  "mcpServers": {
    "mingli": {
      "command": "uvx",
      "args": ["mingli-mcp"],
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Docker部署（HTTP模式）
```bash
docker run -e TRANSPORT_TYPE=http -e HTTP_PORT=8080 mingli-mcp
```

## 配置优先级

1. 环境变量
2. .env文件
3. 默认值

所有配置都有合理的默认值，确保开箱即用。
"""

    def _get_heavenly_stems_content(self) -> str:
        """获取天干地支内容"""
        return """# 天干地支对照表

## 十天干

| 天干 | 五行 | 阴阳 | 属性 |
|------|------|------|------|
| 甲 | 木 | 阳 | 大树之木 |
| 乙 | 木 | 阴 | 花草之木 |
| 丙 | 火 | 阳 | 太阳之火 |
| 丁 | 火 | 阴 | 灯烛之火 |
| 戊 | 土 | 阳 | 城墙之土 |
| 己 | 土 | 阴 | 田园之土 |
| 庚 | 金 | 阳 | 刀剑之金 |
| 辛 | 金 | 阴 | 珠玉之金 |
| 壬 | 水 | 阳 | 江河之水 |
| 癸 | 水 | 阴 | 雨露之水 |

## 十二地支

| 地支 | 五行 | 阴阳 | 生肖 | 时辰 |
|------|------|------|------|------|
| 子 | 水 | 阳 | 鼠 | 23:00-01:00 |
| 丑 | 土 | 阴 | 牛 | 01:00-03:00 |
| 寅 | 木 | 阳 | 虎 | 03:00-05:00 |
| 卯 | 木 | 阴 | 兔 | 05:00-07:00 |
| 辰 | 土 | 阳 | 龙 | 07:00-09:00 |
| 巳 | 火 | 阴 | 蛇 | 09:00-11:00 |
| 午 | 火 | 阳 | 马 | 11:00-13:00 |
| 未 | 土 | 阴 | 羊 | 13:00-15:00 |
| 申 | 金 | 阳 | 猴 | 15:00-17:00 |
| 酉 | 金 | 阴 | 鸡 | 17:00-19:00 |
| 戌 | 土 | 阳 | 狗 | 19:00-21:00 |
| 亥 | 水 | 阴 | 猪 | 21:00-23:00 |

## 天干地支配合

十天干配十二地支，形成六十甲子的循环组合，用于纪年、纪月、纪日、纪时。
"""

    def _get_five_elements_content(self) -> str:
        """获取五行内容"""
        return """# 五行相生相克

## 五行特性

### 木
- **特性**：生长、升发、条达舒畅
- **象征**：东方、春季、青色、肝胆
- **相生**：水生木
- **相克**：金克木

### 火
- **特性**：温热、向上、光明
- **象征**：南方、夏季、红色、心脏
- **相生**：木生火
- **相克**：水克火

### 土
- **特性**：承载、包容、生化万物
- **象征**：中央、长夏、黄色、脾胃
- **相生**：火生土
- **相克**：木克土

### 金
- **特性**：收敛、肃杀、清洁
- **象征**：西方、秋季、白色、肺脏
- **相生**：土生金
- **相克**：火克金

### 水
- **特性**：滋润、向下、寒凉
- **象征**：北方、冬季、黑色、肾脏
- **相生**：金生水
- **相克**：土克水

## 相生循环

木 → 火 → 土 → 金 → 水 → 木

## 相克循环

木 → 土 → 水 → 火 → 金 → 木
"""

    def _get_twelve_palaces_content(self) -> str:
        """获取十二宫位内容"""
        return """# 紫微斗数十二宫位

## 宫位详解

### 1. 命宫
- **主事**：命运、性格、整体格局
- **位置**：寅宫（农历正月）

### 2. 兄弟宫
- **主事**：兄弟姐妹、朋友关系
- **位置**：卯宫（农历二月）

### 3. 夫妻宫
- **主事**：配偶、婚姻、感情
- **位置**：辰宫（农历三月）

### 4. 子女宫
- **主事**：子女、创作、才华
- **位置**：巳宫（农历四月）

### 5. 财帛宫
- **主事**：财富、收入、理财能力
- **位置**：午宫（农历五月）

### 6. 疾厄宫
- **主事**：健康、疾病、意外
- **位置**：未宫（农历六月）

### 7. 迁移宫
- **主事**：外出、迁移、人际关系
- **位置**：申宫（农历七月）

### 8. 奴仆宫
- **主事**：下属、朋友、合作
- **位置**：酉宫（农历八月）

### 9. 官禄宫
- **主事**：事业、工作、地位
- **位置**：戌宫（农历九月）

### 10. 田宅宫
- **主事**：不动产、房产、家庭
- **位置**：亥宫（农历十月）

### 11. 福德宫
- **主事**：福气、享受、心情
- **位置**：子宫（农历十一月）

### 12. 父母宫
- **主事**：父母、长辈、上司
- **位置**：丑宫（农历十二月）
"""

    def _get_ziwei_main_stars_content(self) -> str:
        """获取紫微主星内容"""
        return """# 紫微斗数十四主星

## 帝座星

### 紫微星
- **特性**：帝座之星，主贵气
- **影响**：领导能力、权威地位

### 天机星
- **特性**：智慧之星，主机谋
- **影响**：聪明才智、策划能力

### 太阳星
- **特性**：光明之星，主名声
- **影响**：开朗大方、知名度

## 财星

### 武曲星
- **特性**：财富之星，主财运
- **影响**：理财能力、财务状况

### 天同星
- **特性**：福气之星，主享受
- **影响**：生活享受、人缘关系

### 廉贞星
- **特性**：桃花之星，主感情
- **影响**：感情魅力、人际关系

## 辅星

### 天府星
- **特性**：宝库之星，主财库
- **影响**：积累财富、稳重保守

### 太阴星
- **特性**：月亮之星，主温柔
- **影响**：温柔体贴、直觉敏锐

### 贪狼星
- **特性**：欲望之星，主变化
- **影响**：多才多艺、变化多端

### 巨门星
- **特性**：暗星，主口舌
- **影响**：口才表达、与人争辩

### 天相星
- **特性**：印星，主贵人
- **影响**：贵人帮助、地位尊崇

### 天梁星
- **特性**：荫星，主长辈
- **影响**：长辈缘分、化解灾难

### 七杀星
- **特性**：煞星，主权威
- **影响**：权威果断、波动较大

### 破军星
- **特性**：耗星，主开创
- **影响**：开创破旧、变化激烈
"""

    def _get_time_periods_content(self) -> str:
        """获取时辰对照表内容"""
        return """# 十二时辰对照表

## 时辰详解

| 时辰 | 时间 | 别称 | 地支 | 特征 |
|------|------|------|------|------|
| 子时 | 23:00-01:00 | 夜半、子夜 | 子 | 阴阳交替时 |
| 丑时 | 01:00-03:00 | 鸡鸣 | 丑 | 夜深人静时 |
| 寅时 | 03:00-05:00 | 平旦 | 寅 | 黎明前的黑暗 |
| 卯时 | 05:00-07:00 | 日出 | 卯 | 日出时分 |
| 辰时 | 07:00-09:00 | 食时 | 辰 | 早餐时间 |
| 巳时 | 09:00-11:00 | 隅中 | 巳 | 临近中午 |
| 午时 | 11:00-13:00 | 日中 | 午 | 正午时分 |
| 未时 | 13:00-15:00 | 日昳 | 未 | 午后时分 |
| 申时 | 15:00-17:00 | 晡时 | 申 | 下午茶时间 |
| 酉时 | 17:00-19:00 | 日入 | 酉 | 日落时分 |
| 戌时 | 19:00-21:00 | 黄昏 | 戌 | 傍晚时分 |
| 亥时 | 21:00-23:00 | 人定 | 亥 | 夜深人静时 |

## 现代对应

古代一个时辰 = 现代2小时
古代一刻 = 现代15分钟

## 时辰与出生

根据出生时辰推算时干：
- 子时：甲或己日 = 甲子，乙或庚日 = 丙子，丙或辛日 = 戊子，丁或壬日 = 庚子，戊或癸日 = 壬子
- 丑时：甲或己日 = 乙丑，乙或庚日 = 丁丑，丙或辛日 = 己丑，丁或壬日 = 辛丑，戊或癸日 = 癸丑

（其余时辰依此类推）
"""

    def _get_fortune_terms_content(self) -> str:
        """获取命理术语内容"""
        return """# 命理术语表

## 基础术语

### 天干地支
- **天干**：甲乙丙丁戊己庚辛壬癸十天干
- **地支**：子丑寅卯辰巳午未申酉戌亥十二地支
- **干支**：天干地支的组合，如甲子、乙丑等

### 四柱
- **年柱**：出生年的天干地支
- **月柱**：出生月的天干地支
- **日柱**：出生日的天干地支（日主所在）
- **时柱**：出生时的天干地支

### 五行
- **五行**：金木水火土五种基本元素
- **相生**：水生木，木生火，火生土，土生金，金生水
- **相克**：水克火，火克金，金克木，木克土，土克水

## 十神

### 官杀
- **正官**：克制日主正当的克制力，代表丈夫、地位
- **偏官（七杀）**：克制日主偏激的克制力，代表压力、小人

### 财星
- **正财**：日主所克的正当之财，代表妻子、工资
- **偏财**：日主所克的偏财，代表横财、情人

### 食伤
- **食神**：日主所生之泄秀之星，代表才华、子女
- **伤官**：日主所生之克制官星的星，代表叛逆、克夫

### 比劫
- **比肩**：与日主同类同性，代表兄弟姐妹、朋友
- **劫财**：与日主同类异性，代表争夺、破财

### 印星
- **正印**：生日主之母星，代表母亲、学问、贵人
- **偏印**：生日主之偏星，代表继母、偏门学问

## 常用术语

### 起运
- **大运**：每十年一个运势周期
- **流年**：每一年的运势
- **流月**：每一月的运势
- **流日**：每一日的运势
- **流时**：每一时的运势

### 格局
- **正格**：八种基本格局
- **变格**：特殊的格局变化
- **从格**：日主极弱时的特殊格局

### 用神
- **用神**：对命局有利的五行
- **忌神**：对命局不利的五行
- **喜神**：有帮助用神作用的五行
- **闲神**：中性，对命局影响较小的五行

### 神煞
- **吉神**：带来好运的神煞
- **凶神**：带来不利的神煞
- **桃花**：代表感情、人缘的神煞
- **驿马**：代表变动、迁移的神煞
"""


def main():
    """主函数"""
    try:
        server = MingliMCPServer()
        server.start()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception:
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
