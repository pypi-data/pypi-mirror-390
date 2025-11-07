"""
FakeMCP 自定义异常类

定义了 FakeMCP 系统中使用的所有自定义异常类型，
提供统一的错误处理和错误响应格式。
"""

from typing import Any, Dict, List, Optional


class FakeMCPError(Exception):
    """FakeMCP 基础异常类"""
    
    def __init__(
        self,
        message: str,
        error_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type or self.__class__.__name__
        self.details = details or {}
        self.suggestions = suggestions or []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于 MCP 响应"""
        return {
            "success": False,
            "error": {
                "type": self.error_type,
                "message": self.message,
                "details": self.details,
                "suggestions": self.suggestions
            }
        }


class ConnectionError(FakeMCPError):
    """连接错误：无法连接到目标 MCP 服务器"""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "检查目标 MCP 服务器是否正在运行",
            "验证 URL 是否正确",
            "检查网络连接",
            "确认认证配置是否正确"
        ]
        error_details = details or {}
        if url:
            error_details["url"] = url
        
        super().__init__(
            message=message,
            error_type="ConnectionError",
            details=error_details,
            suggestions=suggestions
        )


class SchemaError(FakeMCPError):
    """Schema 错误：Schema 解析或验证失败"""
    
    def __init__(
        self,
        message: str,
        schema_source: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "检查目标 MCP 服务器返回的 Schema 格式",
            "确认 Schema 符合 MCP 协议规范",
            "尝试手动提供 Schema 定义"
        ]
        error_details = details or {}
        if schema_source:
            error_details["schema_source"] = schema_source
        
        super().__init__(
            message=message,
            error_type="SchemaError",
            details=error_details,
            suggestions=suggestions
        )


class ValidationError(FakeMCPError):
    """验证错误：数据验证失败"""
    
    def __init__(
        self,
        message: str,
        validation_errors: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "检查数据格式是否符合 Schema 定义",
            "验证必填字段是否存在",
            "确认数据类型是否正确"
        ]
        error_details = details or {}
        if validation_errors:
            error_details["validation_errors"] = validation_errors
        
        super().__init__(
            message=message,
            error_type="ValidationError",
            details=error_details,
            suggestions=suggestions
        )


class ActorNotFoundError(FakeMCPError):
    """角色未找到错误：请求的角色不存在"""
    
    def __init__(
        self,
        message: str,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "使用 list_actors 工具查看所有可用角色",
            "使用 add_actor_config 工具添加角色配置",
            "检查角色类型和 ID 是否正确"
        ]
        error_details = details or {}
        if actor_type:
            error_details["actor_type"] = actor_type
        if actor_id:
            error_details["actor_id"] = actor_id
        
        super().__init__(
            message=message,
            error_type="ActorNotFoundError",
            details=error_details,
            suggestions=suggestions
        )


class ScenarioNotFoundError(FakeMCPError):
    """场景未找到错误：请求的场景不存在"""
    
    def __init__(
        self,
        message: str,
        scenario_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "使用 set_scenario 工具创建新场景",
            "使用 load_scenario 工具加载已保存的场景",
            "检查场景 ID 是否正确"
        ]
        error_details = details or {}
        if scenario_id:
            error_details["scenario_id"] = scenario_id
        
        super().__init__(
            message=message,
            error_type="ScenarioNotFoundError",
            details=error_details,
            suggestions=suggestions
        )


class DataGenerationError(FakeMCPError):
    """数据生成错误：模拟数据生成失败"""
    
    def __init__(
        self,
        message: str,
        target_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "检查角色配置是否完整",
            "验证场景描述是否清晰",
            "确认目标 MCP Schema 是否正确",
            "尝试提供更多真实数据示例"
        ]
        error_details = details or {}
        if target_id:
            error_details["target_id"] = target_id
        if tool_name:
            error_details["tool_name"] = tool_name
        
        super().__init__(
            message=message,
            error_type="DataGenerationError",
            details=error_details,
            suggestions=suggestions
        )


class PlotConsistencyError(FakeMCPError):
    """剧情一致性错误：剧情图存在逻辑问题"""
    
    def __init__(
        self,
        message: str,
        issues: Optional[List[Dict[str, Any]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "检查因果关系是否存在循环依赖",
            "验证时间线是否一致",
            "确认所有涉及的角色都已配置"
        ]
        error_details = details or {}
        if issues:
            error_details["issues"] = issues
        
        super().__init__(
            message=message,
            error_type="PlotConsistencyError",
            details=error_details,
            suggestions=suggestions
        )


class ToolNotFoundError(FakeMCPError):
    """工具未找到错误：请求的工具不存在"""
    
    def __init__(
        self,
        message: str,
        tool_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "检查工具名称是否正确",
            "使用 MCP 协议查询可用工具列表",
            "确认目标 MCP 服务器是否支持该工具"
        ]
        error_details = details or {}
        if tool_name:
            error_details["tool_name"] = tool_name
        
        super().__init__(
            message=message,
            error_type="ToolNotFoundError",
            details=error_details,
            suggestions=suggestions
        )


class TargetMCPNotFoundError(FakeMCPError):
    """目标 MCP 未找到错误：请求的目标 MCP 不存在"""
    
    def __init__(
        self,
        message: str,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "使用 add_target_mcp 工具添加目标 MCP",
            "使用 get_scenario_status 工具查看已添加的目标 MCP",
            "检查目标 MCP ID 是否正确"
        ]
        error_details = details or {}
        if target_id:
            error_details["target_id"] = target_id
        
        super().__init__(
            message=message,
            error_type="TargetMCPNotFoundError",
            details=error_details,
            suggestions=suggestions
        )


class FileOperationError(FakeMCPError):
    """文件操作错误：场景保存或加载失败"""
    
    def __init__(
        self,
        message: str,
        filepath: Optional[str] = None,
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "检查文件路径是否正确",
            "验证文件权限",
            "确认文件格式是否正确（YAML）",
            "检查磁盘空间是否充足"
        ]
        error_details = details or {}
        if filepath:
            error_details["filepath"] = filepath
        if operation:
            error_details["operation"] = operation
        
        super().__init__(
            message=message,
            error_type="FileOperationError",
            details=error_details,
            suggestions=suggestions
        )


class WorkflowError(FakeMCPError):
    """工作流错误：工作流状态或操作错误"""
    
    def __init__(
        self,
        message: str,
        current_stage: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        suggestions = [
            "使用 guide 工具查看当前工作流状态",
            "按照工作流顺序完成各个阶段",
            "如需重新开始，使用 guide 工具的 reset 操作"
        ]
        error_details = details or {}
        if current_stage:
            error_details["current_stage"] = current_stage
        
        super().__init__(
            message=message,
            error_type="WorkflowError",
            details=error_details,
            suggestions=suggestions
        )


def format_error_response(error: Exception) -> Dict[str, Any]:
    """
    格式化错误响应
    
    将任何异常转换为统一的错误响应格式。
    如果是 FakeMCPError，使用其 to_dict 方法；
    否则创建通用错误响应。
    
    Args:
        error: 异常对象
        
    Returns:
        统一格式的错误响应字典
    """
    if isinstance(error, FakeMCPError):
        return error.to_dict()
    
    # 处理标准异常
    return {
        "success": False,
        "error": {
            "type": type(error).__name__,
            "message": str(error),
            "details": {},
            "suggestions": ["检查输入参数", "查看日志获取更多信息"]
        }
    }
