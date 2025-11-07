"""
Tests for MCP Server implementation
"""

import pytest
from unittest.mock import AsyncMock
from fakemcp.mcp_server import MCPServer, get_server, register_tool


@pytest.mark.asyncio
async def test_mcp_server_initialization():
    """测试 MCP 服务器初始化"""
    server = MCPServer()
    assert server is not None
    assert server.server is not None
    assert isinstance(server.tool_handlers, dict)
    assert len(server.tool_handlers) == 0


@pytest.mark.asyncio
async def test_register_tool():
    """测试工具注册"""
    server = MCPServer()
    
    async def test_handler(args):
        return {"result": "success"}
    
    server.register_tool(
        name="test_tool",
        description="A test tool",
        input_schema={
            "type": "object",
            "properties": {
                "param": {"type": "string"}
            }
        },
        handler=test_handler
    )
    
    assert "test_tool" in server.tool_handlers
    assert server.tool_handlers["test_tool"].name == "test_tool"
    assert server.tool_handlers["test_tool"].description == "A test tool"


@pytest.mark.asyncio
async def test_unregister_tool():
    """测试工具注销"""
    server = MCPServer()
    
    async def test_handler(args):
        return {"result": "success"}
    
    server.register_tool(
        name="test_tool",
        description="A test tool",
        input_schema={"type": "object"},
        handler=test_handler
    )
    
    assert "test_tool" in server.tool_handlers
    
    server.unregister_tool("test_tool")
    assert "test_tool" not in server.tool_handlers


@pytest.mark.asyncio
async def test_get_registered_tools():
    """测试获取已注册工具列表"""
    server = MCPServer()
    
    async def handler1(args):
        return {}
    
    async def handler2(args):
        return {}
    
    server.register_tool("tool1", "Tool 1", {"type": "object"}, handler1)
    server.register_tool("tool2", "Tool 2", {"type": "object"}, handler2)
    
    tools = server.get_registered_tools()
    assert len(tools) == 2
    assert "tool1" in tools
    assert "tool2" in tools


@pytest.mark.asyncio
async def test_get_server_singleton():
    """测试全局服务器实例单例模式"""
    server1 = get_server()
    server2 = get_server()
    assert server1 is server2


@pytest.mark.asyncio
async def test_register_tool_convenience_function():
    """测试便捷注册函数"""
    async def test_handler(args):
        return {"result": "ok"}
    
    register_tool(
        name="convenience_tool",
        description="Test convenience function",
        input_schema={"type": "object"},
        handler=test_handler
    )
    
    server = get_server()
    assert "convenience_tool" in server.tool_handlers
