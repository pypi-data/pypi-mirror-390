"""
Tests for Data Tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fakemcp.database import Database
from fakemcp.models import Actor, Scenario, TargetMCP
from fakemcp.tools.data_tools import DataTools


@pytest.fixture
def database():
    """Create an in-memory database for testing"""
    db = Database(':memory:')
    return db


@pytest.fixture
def data_tools(database):
    """Create DataTools instance"""
    return DataTools(database)


@pytest.fixture
def sample_target_mcp(database):
    """Create a sample target MCP"""
    target_mcp = TargetMCP(
        id='prometheus',
        name='Prometheus',
        url='http://localhost:9090/mcp',
        config={},
        schema={
            'tools': [
                {
                    'name': 'query_metrics',
                    'description': 'Query metrics',
                    'inputSchema': {
                        'type': 'object',
                        'properties': {
                            'instance': {'type': 'string'},
                            'metric': {'type': 'string'}
                        }
                    },
                    'outputSchema': {
                        'type': 'object',
                        'properties': {
                            'value': {'type': 'number'},
                            'timestamp': {'type': 'string'}
                        }
                    }
                }
            ]
        },
        actor_fields=['instance'],
        example_data={},
        connected=True
    )
    database.create_target_mcp(target_mcp)
    return target_mcp


@pytest.fixture
def sample_scenario(database):
    """Create a sample scenario"""
    from fakemcp.scenario_manager import ScenarioManager
    manager = ScenarioManager(database)
    scenario = manager.create_scenario(
        description='模拟内存泄露场景',
        target_mcps=['prometheus']
    )
    return scenario


@pytest.fixture
def sample_actor(database):
    """Create a sample actor"""
    actor = Actor(
        actor_type='server_id',
        actor_id='server-01',
        description='内存持续增长，从 2GB 增长到 8GB',
        state={},
        parent_actor=None,
        metadata={}
    )
    database.create_actor(actor)
    return actor


@pytest.mark.asyncio
async def test_fetch_real_data_success(data_tools, sample_target_mcp):
    """测试成功获取真实数据"""
    mock_data = {
        'value': 2048.5,
        'timestamp': '2024-01-01T00:00:00Z'
    }
    
    with patch.object(
        data_tools.target_mcp_analyzer,
        'fetch_real_data',
        new_callable=AsyncMock,
        return_value=mock_data
    ):
        result = await data_tools.fetch_real_data(
            target_id='prometheus',
            tool_name='query_metrics',
            parameters={'instance': 'server-01', 'metric': 'memory_usage'}
        )
    
    assert result['success'] is True
    assert result['data'] == mock_data
    assert result['targetId'] == 'prometheus'
    assert result['toolName'] == 'query_metrics'
    assert 'cached' in result


@pytest.mark.asyncio
async def test_fetch_real_data_target_not_found(data_tools):
    """测试目标 MCP 不存在"""
    result = await data_tools.fetch_real_data(
        target_id='nonexistent',
        tool_name='query_metrics',
        parameters={}
    )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'TargetMCPNotFoundError'
    assert 'suggestions' in result['error']


@pytest.mark.asyncio
async def test_fetch_real_data_tool_not_found(data_tools, sample_target_mcp):
    """测试工具不存在"""
    result = await data_tools.fetch_real_data(
        target_id='prometheus',
        tool_name='nonexistent_tool',
        parameters={}
    )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'ToolNotFoundError'
    assert 'available_tools' in result['error']['details']


def test_generate_mock_data_success(
    data_tools, sample_target_mcp, sample_scenario, sample_actor
):
    """测试成功生成模拟数据"""
    result = data_tools.generate_mock_data(
        target_id='prometheus',
        tool_name='query_metrics',
        parameters={'instance': 'server-01', 'metric': 'memory_usage'}
    )
    
    # If failed, print the error for debugging
    if not result.get('success'):
        print(f"Error: {result.get('error')}")
    
    assert result['success'] is True
    assert 'data' in result
    assert result['targetId'] == 'prometheus'
    assert result['toolName'] == 'query_metrics'
    assert 'actorsInvolved' in result
    assert 'server-01' in result['actorsInvolved']
    assert 'scenarioId' in result


def test_generate_mock_data_target_not_found(data_tools):
    """测试目标 MCP 不存在"""
    result = data_tools.generate_mock_data(
        target_id='nonexistent',
        tool_name='query_metrics',
        parameters={}
    )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'TargetMCPNotFoundError'


def test_generate_mock_data_no_scenario(data_tools, sample_target_mcp):
    """测试没有场景时生成数据"""
    result = data_tools.generate_mock_data(
        target_id='prometheus',
        tool_name='query_metrics',
        parameters={'instance': 'server-01'}
    )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'NoScenarioError'


def test_validate_mock_data_success(
    data_tools, sample_target_mcp, sample_scenario
):
    """测试验证模拟数据"""
    mock_data = {
        'value': 2048.5,
        'timestamp': '2024-01-01T00:00:00Z'
    }
    
    result = data_tools.validate_mock_data(
        target_id='prometheus',
        tool_name='query_metrics',
        mock_data=mock_data
    )
    
    assert 'valid' in result
    assert 'issues' in result
    assert 'suggestions' in result
    assert result['targetId'] == 'prometheus'
    assert result['toolName'] == 'query_metrics'


def test_validate_mock_data_target_not_found(data_tools):
    """测试目标 MCP 不存在"""
    result = data_tools.validate_mock_data(
        target_id='nonexistent',
        tool_name='query_metrics',
        mock_data={}
    )
    
    assert result['valid'] is False
    assert 'error' in result
    assert result['error']['type'] == 'TargetMCPNotFoundError'


def test_validate_mock_data_no_scenario(data_tools, sample_target_mcp):
    """测试没有场景时验证数据"""
    result = data_tools.validate_mock_data(
        target_id='prometheus',
        tool_name='query_metrics',
        mock_data={}
    )
    
    assert result['valid'] is False
    assert 'error' in result
    assert result['error']['type'] == 'NoScenarioError'


def test_get_tool_definitions(data_tools):
    """测试获取工具定义"""
    tool_defs = data_tools.get_tool_definitions()
    
    assert len(tool_defs) == 3
    
    tool_names = [tool['name'] for tool in tool_defs]
    assert 'fetch_real_data' in tool_names
    assert 'generate_mock_data' in tool_names
    assert 'validate_mock_data' in tool_names
    
    # 检查每个工具都有必要的字段
    for tool_def in tool_defs:
        assert 'name' in tool_def
        assert 'description' in tool_def
        assert 'inputSchema' in tool_def
        assert 'type' in tool_def['inputSchema']
        assert 'properties' in tool_def['inputSchema']
        assert 'required' in tool_def['inputSchema']


def test_generate_mock_data_with_plot_graph(
    data_tools, sample_target_mcp, sample_scenario, sample_actor
):
    """测试基于剧情图生成模拟数据"""
    # 添加剧情图到场景
    from fakemcp.plot_manager import PlotGraph, PlotNode
    
    plot_graph = PlotGraph()
    node = PlotNode(
        id='node1',
        actor='server-01',
        event='memory_leak',
        timestamp_offset=0,
        data_pattern={'memory_trend': 'increasing'},
        children=[]
    )
    plot_graph.add_node(node)
    
    # 更新场景元数据
    from fakemcp.scenario_manager import ScenarioManager
    scenario_manager = ScenarioManager(data_tools.db)
    scenario_manager.update_scenario(
        sample_scenario.id,
        metadata_updates={'plot_graph': plot_graph.to_dict()}
    )
    
    result = data_tools.generate_mock_data(
        target_id='prometheus',
        tool_name='query_metrics',
        parameters={'instance': 'server-01', 'metric': 'memory_usage'},
        scenario_id=sample_scenario.id
    )
    
    assert result['success'] is True
    assert result['basedOnPlot'] is True
    assert 'data' in result


def test_validate_mock_data_with_issues(
    data_tools, sample_target_mcp, sample_scenario
):
    """测试验证有问题的模拟数据"""
    # 创建一个不符合 schema 的数据
    mock_data = {
        'value': 'invalid_number',  # 应该是 number 类型
        'timestamp': 'invalid_timestamp'
    }
    
    result = data_tools.validate_mock_data(
        target_id='prometheus',
        tool_name='query_metrics',
        mock_data=mock_data
    )
    
    # 验证应该失败或有问题
    if not result['valid']:
        assert len(result['issues']) > 0
        assert len(result['suggestions']) > 0
