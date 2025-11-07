"""
自定义异常类

定义项目中使用的所有异常类型，提供更精确的错误处理
"""


class MingliMCPError(Exception):
    """
    基础异常类

    所有自定义异常的基类
    """

    pass


class ValidationError(MingliMCPError):
    """
    参数验证错误

    当输入参数不符合要求时抛出
    例如：日期格式错误、时辰超出范围、性别无效等
    """

    pass


class SystemError(MingliMCPError):
    """
    系统执行错误

    当命理系统执行过程中发生错误时抛出
    例如：排盘计算失败、运势查询失败等
    """

    pass


class SystemNotFoundError(MingliMCPError):
    """
    系统未找到错误

    当请求的命理系统未注册时抛出
    """

    pass


class ConfigError(MingliMCPError):
    """
    配置错误

    当配置项缺失或无效时抛出
    """

    pass


class TransportError(MingliMCPError):
    """
    传输层错误

    当传输层通信出现问题时抛出
    """

    pass


class DependencyError(MingliMCPError):
    """
    依赖错误

    当必需的第三方库未安装或版本不兼容时抛出
    """

    pass


class ToolCallError(MingliMCPError):
    """
    工具调用错误

    当MCP工具调用失败时抛出
    """

    pass


class FormatError(MingliMCPError):
    """
    格式化错误

    当数据格式化失败时抛出
    """

    pass
