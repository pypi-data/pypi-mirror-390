"""
Tests for error handling system
"""

import pytest
from fakemcp.errors import (
    FakeMCPError,
    ConnectionError,
    SchemaError,
    ValidationError,
    ActorNotFoundError,
    ScenarioNotFoundError,
    DataGenerationError,
    PlotConsistencyError,
    ToolNotFoundError,
    TargetMCPNotFoundError,
    FileOperationError,
    WorkflowError,
    format_error_response
)


def test_base_error():
    """测试基础异常类"""
    error = FakeMCPError(
        message="Test error",
        error_type="TestError",
        details={"key": "value"},
        suggestions=["suggestion 1", "suggestion 2"]
    )
    
    assert str(error) == "Test error"
    assert error.error_type == "TestError"
    assert error.details == {"key": "value"}
    assert error.suggestions == ["suggestion 1", "suggestion 2"]
    
    # 测试 to_dict
    error_dict = error.to_dict()
    assert error_dict["success"] is False
    assert error_dict["error"]["type"] == "TestError"
    assert error_dict["error"]["message"] == "Test error"
    assert error_dict["error"]["details"] == {"key": "value"}
    assert error_dict["error"]["suggestions"] == ["suggestion 1", "suggestion 2"]


def test_connection_error():
    """测试连接错误"""
    error = ConnectionError(
        message="Failed to connect",
        url="http://example.com"
    )
    
    assert str(error) == "Failed to connect"
    assert error.error_type == "ConnectionError"
    assert error.details["url"] == "http://example.com"
    assert len(error.suggestions) > 0


def test_schema_error():
    """测试 Schema 错误"""
    error = SchemaError(
        message="Invalid schema",
        schema_source="http://example.com"
    )
    
    assert str(error) == "Invalid schema"
    assert error.error_type == "SchemaError"
    assert error.details["schema_source"] == "http://example.com"
    assert len(error.suggestions) > 0


def test_validation_error():
    """测试验证错误"""
    validation_errors = ["Field 'name' is required", "Field 'age' must be a number"]
    error = ValidationError(
        message="Validation failed",
        validation_errors=validation_errors
    )
    
    assert str(error) == "Validation failed"
    assert error.error_type == "ValidationError"
    assert error.details["validation_errors"] == validation_errors
    assert len(error.suggestions) > 0


def test_actor_not_found_error():
    """测试角色未找到错误"""
    error = ActorNotFoundError(
        message="Actor not found",
        actor_type="server",
        actor_id="server-01"
    )
    
    assert str(error) == "Actor not found"
    assert error.error_type == "ActorNotFoundError"
    assert error.details["actor_type"] == "server"
    assert error.details["actor_id"] == "server-01"
    assert len(error.suggestions) > 0


def test_scenario_not_found_error():
    """测试场景未找到错误"""
    error = ScenarioNotFoundError(
        message="Scenario not found",
        scenario_id="scenario-123"
    )
    
    assert str(error) == "Scenario not found"
    assert error.error_type == "ScenarioNotFoundError"
    assert error.details["scenario_id"] == "scenario-123"
    assert len(error.suggestions) > 0


def test_data_generation_error():
    """测试数据生成错误"""
    error = DataGenerationError(
        message="Failed to generate data",
        target_id="target-1",
        tool_name="get_metrics"
    )
    
    assert str(error) == "Failed to generate data"
    assert error.error_type == "DataGenerationError"
    assert error.details["target_id"] == "target-1"
    assert error.details["tool_name"] == "get_metrics"
    assert len(error.suggestions) > 0


def test_plot_consistency_error():
    """测试剧情一致性错误"""
    issues = [
        {"type": "circular_dependency", "nodes": ["A", "B", "A"]},
        {"type": "time_conflict", "nodes": ["C", "D"]}
    ]
    error = PlotConsistencyError(
        message="Plot has consistency issues",
        issues=issues
    )
    
    assert str(error) == "Plot has consistency issues"
    assert error.error_type == "PlotConsistencyError"
    assert error.details["issues"] == issues
    assert len(error.suggestions) > 0


def test_tool_not_found_error():
    """测试工具未找到错误"""
    error = ToolNotFoundError(
        message="Tool not found",
        tool_name="unknown_tool"
    )
    
    assert str(error) == "Tool not found"
    assert error.error_type == "ToolNotFoundError"
    assert error.details["tool_name"] == "unknown_tool"
    assert len(error.suggestions) > 0


def test_target_mcp_not_found_error():
    """测试目标 MCP 未找到错误"""
    error = TargetMCPNotFoundError(
        message="Target MCP not found",
        target_id="target-123"
    )
    
    assert str(error) == "Target MCP not found"
    assert error.error_type == "TargetMCPNotFoundError"
    assert error.details["target_id"] == "target-123"
    assert len(error.suggestions) > 0


def test_file_operation_error():
    """测试文件操作错误"""
    error = FileOperationError(
        message="Failed to save file",
        filepath="/path/to/file.yaml",
        operation="save"
    )
    
    assert str(error) == "Failed to save file"
    assert error.error_type == "FileOperationError"
    assert error.details["filepath"] == "/path/to/file.yaml"
    assert error.details["operation"] == "save"
    assert len(error.suggestions) > 0


def test_workflow_error():
    """测试工作流错误"""
    error = WorkflowError(
        message="Invalid workflow state",
        current_stage="data_generation"
    )
    
    assert str(error) == "Invalid workflow state"
    assert error.error_type == "WorkflowError"
    assert error.details["current_stage"] == "data_generation"
    assert len(error.suggestions) > 0


def test_format_error_response_with_fakemcp_error():
    """测试格式化 FakeMCP 错误响应"""
    error = ActorNotFoundError(
        message="Actor not found",
        actor_type="server",
        actor_id="server-01"
    )
    
    response = format_error_response(error)
    
    assert response["success"] is False
    assert response["error"]["type"] == "ActorNotFoundError"
    assert response["error"]["message"] == "Actor not found"
    assert response["error"]["details"]["actor_type"] == "server"
    assert response["error"]["details"]["actor_id"] == "server-01"
    assert len(response["error"]["suggestions"]) > 0


def test_format_error_response_with_standard_exception():
    """测试格式化标准异常响应"""
    error = ValueError("Invalid value")
    
    response = format_error_response(error)
    
    assert response["success"] is False
    assert response["error"]["type"] == "ValueError"
    assert response["error"]["message"] == "Invalid value"
    assert response["error"]["details"] == {}
    assert len(response["error"]["suggestions"]) > 0


def test_error_inheritance():
    """测试错误继承关系"""
    error = ConnectionError(message="Test")
    
    assert isinstance(error, FakeMCPError)
    assert isinstance(error, Exception)
