"""
响应格式化工具
"""

from typing import Any, Dict, Optional


def format_error_response(
    error_code: int, error_message: str, request_id: Optional[Any] = None
) -> Dict[str, Any]:
    """
    格式化错误响应

    Args:
        error_code: 错误代码
        error_message: 错误消息
        request_id: 请求ID

    Returns:
        JSON-RPC错误响应
    """
    response = {"jsonrpc": "2.0", "error": {"code": error_code, "message": error_message}}

    if request_id is not None:
        response["id"] = request_id

    return response


def format_success_response(result: Any, request_id: Optional[Any] = None) -> Dict[str, Any]:
    """
    格式化成功响应

    Args:
        result: 结果数据
        request_id: 请求ID

    Returns:
        JSON-RPC成功响应
    """
    response = {"jsonrpc": "2.0", "result": result}

    if request_id is not None:
        response["id"] = request_id

    return response
