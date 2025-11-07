"""
Integration tests for Guide Tool with MCP Server
"""

import pytest
from fakemcp.config import Config
from fakemcp.database import Database
from fakemcp.mcp_server import MCPServer
from fakemcp.tools.guide_tool import GuideTools


@pytest.fixture
def database():
    """创建测试数据库"""
    db = Database(':memory:')
    yield db


@pytest.fixture
def mcp_server():
    """创建 MCP 服务器实例"""
    return MCPServer()


@pytest.fixture
def guide_tools(database):
    """创建 GuideTools 实例"""
    return GuideTools(database)


@pytest.mark.asyncio
async def test_guide_tool_registration(mcp_server, guide_tools):
    """测试 guide 工具注册到 MCP 服务器"""
    # 获取工具定义
    tool_defs = guide_tools.get_tool_definitions()
    
    # 注册工具
    for tool_def in tool_defs:
        mcp_server.register_tool(
            name=tool_def['name'],
            description=tool_def['description'],
            input_schema=tool_def['inputSchema'],
            handler=lambda args, t=guide_tools: t.guide(**args)
        )
    
    # 验证工具已注册
    registered_tools = mcp_server.get_registered_tools()
    assert 'guide' in registered_tools


@pytest.mark.asyncio
async def test_guide_tool_execution_via_server(mcp_server, guide_tools):
    """测试通过 MCP 服务器执行 guide 工具"""
    # 注册工具
    tool_defs = guide_tools.get_tool_definitions()
    for tool_def in tool_defs:
        mcp_server.register_tool(
            name=tool_def['name'],
            description=tool_def['description'],
            input_schema=tool_def['inputSchema'],
            handler=lambda args, t=guide_tools: t.guide(**args)
        )
    
    # 通过服务器调用工具
    handler = mcp_server.tool_handlers['guide'].handler
    result = await handler({'action': 'start'})
    
    assert result['success'] is True
    assert result['stage'] == 'init'
    assert 'prompt' in result


@pytest.mark.asyncio
async def test_guide_tool_schema_validation(guide_tools):
    """测试 guide 工具的 schema 定义正确性"""
    tool_defs = guide_tools.get_tool_definitions()
    
    assert len(tool_defs) == 1
    guide_def = tool_defs[0]
    
    # 验证必需字段
    assert 'name' in guide_def
    assert 'description' in guide_def
    assert 'inputSchema' in guide_def
    
    # 验证 schema 结构
    schema = guide_def['inputSchema']
    assert schema['type'] == 'object'
    assert 'properties' in schema
    assert 'action' in schema['properties']
    
    # 验证 action 枚举值
    action_schema = schema['properties']['action']
    assert 'enum' in action_schema
    valid_actions = {'start', 'next', 'status', 'reset'}
    assert set(action_schema['enum']) == valid_actions
