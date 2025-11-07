"""
Tests for Scenario Tools
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from fakemcp.database import Database
from fakemcp.tools.scenario_tools import ScenarioTools


@pytest.fixture
def database():
    """Create an in-memory database for testing"""
    db = Database(':memory:')
    return db


@pytest.fixture
def scenario_tools(database):
    """Create ScenarioTools instance"""
    return ScenarioTools(database)


@pytest.mark.asyncio
async def test_set_scenario(scenario_tools):
    """测试设置场景描述"""
    result = await scenario_tools.set_scenario(
        description='模拟内存泄露场景',
        target_mcps=['prometheus', 'cloudmonitoring']
    )
    
    assert result['success'] is True
    assert 'scenarioId' in result
    assert result['description'] == '模拟内存泄露场景'
    assert result['targetMcps'] == ['prometheus', 'cloudmonitoring']
    assert 'keywords' in result
    assert 'extractedActors' in result


@pytest.mark.asyncio
async def test_set_scenario_without_target_mcps(scenario_tools):
    """测试设置场景描述（不指定目标 MCP）"""
    result = await scenario_tools.set_scenario(
        description='测试场景'
    )
    
    assert result['success'] is True
    assert 'scenarioId' in result
    assert result['targetMcps'] == []


@pytest.mark.asyncio
async def test_set_scenario_extracts_keywords(scenario_tools):
    """测试场景描述关键词提取"""
    result = await scenario_tools.set_scenario(
        description='模拟 server-01 的内存泄露场景，内存从 2GB 增长到 8GB'
    )
    
    assert result['success'] is True
    assert 'keywords' in result
    # 应该提取出一些关键词
    keywords = result['keywords']
    assert len(keywords) > 0


@pytest.mark.asyncio
async def test_add_target_mcp_success(scenario_tools):
    """测试成功添加目标 MCP"""
    # Mock the target_mcp_analyzer.connect method
    mock_target_mcp = MagicMock()
    mock_target_mcp.id = 'prometheus'
    mock_target_mcp.name = 'Prometheus'
    mock_target_mcp.url = 'http://localhost:9090/mcp'
    mock_target_mcp.schema = {'tools': []}
    mock_target_mcp.actor_fields = ['instance', 'job', 'server_id']
    mock_target_mcp.connected = True
    
    with patch.object(
        scenario_tools.target_mcp_analyzer,
        'connect',
        new_callable=AsyncMock,
        return_value=mock_target_mcp
    ):
        result = await scenario_tools.add_target_mcp(
            name='Prometheus',
            url='http://localhost:9090/mcp',
            config={'auth_token': 'test_token'}
        )
    
    assert result['success'] is True
    assert result['targetId'] == 'prometheus'
    assert result['name'] == 'Prometheus'
    assert result['url'] == 'http://localhost:9090/mcp'
    assert 'schema' in result
    assert 'detectedActorFields' in result
    assert result['detectedActorFields'] == ['instance', 'job', 'server_id']
    assert result['connected'] is True


@pytest.mark.asyncio
async def test_add_target_mcp_with_scenario(scenario_tools):
    """测试添加目标 MCP 并关联到场景"""
    # 先创建场景
    scenario_result = await scenario_tools.set_scenario(
        description='测试场景'
    )
    scenario_id = scenario_result['scenarioId']
    
    # Mock the target_mcp_analyzer.connect method
    mock_target_mcp = MagicMock()
    mock_target_mcp.id = 'prometheus'
    mock_target_mcp.name = 'Prometheus'
    mock_target_mcp.url = 'http://localhost:9090/mcp'
    mock_target_mcp.schema = {'tools': []}
    mock_target_mcp.actor_fields = ['instance']
    mock_target_mcp.connected = True
    
    with patch.object(
        scenario_tools.target_mcp_analyzer,
        'connect',
        new_callable=AsyncMock,
        return_value=mock_target_mcp
    ):
        result = await scenario_tools.add_target_mcp(
            name='Prometheus',
            url='http://localhost:9090/mcp',
            scenario_id=scenario_id
        )
    
    assert result['success'] is True
    
    # 验证场景已更新
    scenario = scenario_tools.scenario_manager.get_scenario(scenario_id)
    assert 'prometheus' in scenario.target_mcps


@pytest.mark.asyncio
async def test_add_target_mcp_connection_error(scenario_tools):
    """测试添加目标 MCP 连接失败"""
    # Mock the target_mcp_analyzer.connect to raise an exception
    with patch.object(
        scenario_tools.target_mcp_analyzer,
        'connect',
        new_callable=AsyncMock,
        side_effect=Exception('Connection failed')
    ):
        result = await scenario_tools.add_target_mcp(
            name='Prometheus',
            url='http://invalid:9090/mcp'
        )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'TargetMCPConnectionError'
    assert 'suggestions' in result['error']


def test_get_scenario_status_no_scenario(scenario_tools):
    """测试获取场景状态（没有场景）"""
    result = scenario_tools.get_scenario_status()
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'NoScenarioError'


@pytest.mark.asyncio
async def test_get_scenario_status_with_scenario(scenario_tools):
    """测试获取场景状态（有场景）"""
    # 创建场景
    scenario_result = await scenario_tools.set_scenario(
        description='测试场景'
    )
    scenario_id = scenario_result['scenarioId']
    
    # 获取状态
    result = scenario_tools.get_scenario_status(scenario_id=scenario_id)
    
    assert result['success'] is True
    assert result['scenarioId'] == scenario_id
    assert result['description'] == '测试场景'
    assert 'targetMcps' in result
    assert 'actors' in result
    assert 'causalityRelations' in result
    assert 'ready' in result
    assert 'createdAt' in result
    assert 'updatedAt' in result


@pytest.mark.asyncio
async def test_get_scenario_status_latest(scenario_tools):
    """测试获取最新场景状态（不指定 scenario_id）"""
    # 创建多个场景
    await scenario_tools.set_scenario(description='场景1')
    await scenario_tools.set_scenario(description='场景2')
    result3 = await scenario_tools.set_scenario(description='场景3')
    
    # 获取最新场景状态（不指定 ID）
    status = scenario_tools.get_scenario_status()
    
    assert status['success'] is True
    # 应该返回最新的场景
    assert status['scenarioId'] == result3['scenarioId']
    assert status['description'] == '场景3'


@pytest.mark.asyncio
async def test_get_scenario_status_with_target_mcps(scenario_tools):
    """测试获取场景状态（包含目标 MCP）"""
    # 创建场景
    scenario_result = await scenario_tools.set_scenario(
        description='测试场景'
    )
    scenario_id = scenario_result['scenarioId']
    
    # 添加目标 MCP - 需要同时 mock 和保存到数据库
    from fakemcp.models import TargetMCP
    
    async def mock_connect(target_id, name, url, config):
        # 创建真实的 TargetMCP 对象并保存到数据库
        target_mcp = TargetMCP(
            id=target_id,
            name=name,
            url=url,
            config=config,
            schema={'tools': []},
            actor_fields=['instance'],
            example_data={},
            connected=True
        )
        scenario_tools.db.create_target_mcp(target_mcp)
        return target_mcp
    
    with patch.object(
        scenario_tools.target_mcp_analyzer,
        'connect',
        new_callable=AsyncMock,
        side_effect=mock_connect
    ):
        await scenario_tools.add_target_mcp(
            name='Prometheus',
            url='http://localhost:9090/mcp',
            scenario_id=scenario_id
        )
    
    # 获取状态
    result = scenario_tools.get_scenario_status(scenario_id=scenario_id)
    
    assert result['success'] is True
    assert len(result['targetMcps']) == 1
    assert result['targetMcps'][0]['id'] == 'prometheus'
    assert result['targetMcps'][0]['name'] == 'Prometheus'
    assert result['targetMcps'][0]['connected'] is True


@pytest.mark.asyncio
async def test_get_scenario_status_ready_condition(scenario_tools):
    """测试场景准备就绪条件"""
    # 创建场景
    scenario_result = await scenario_tools.set_scenario(
        description='测试场景'
    )
    scenario_id = scenario_result['scenarioId']
    
    # 初始状态：没有目标 MCP 和角色，不应该 ready
    status1 = scenario_tools.get_scenario_status(scenario_id=scenario_id)
    assert status1['ready'] is False
    
    # 添加目标 MCP - 需要同时 mock 和保存到数据库
    from fakemcp.models import TargetMCP
    
    async def mock_connect(target_id, name, url, config):
        # 创建真实的 TargetMCP 对象并保存到数据库
        target_mcp = TargetMCP(
            id=target_id,
            name=name,
            url=url,
            config=config,
            schema={'tools': []},
            actor_fields=['instance'],
            example_data={},
            connected=True
        )
        scenario_tools.db.create_target_mcp(target_mcp)
        return target_mcp
    
    with patch.object(
        scenario_tools.target_mcp_analyzer,
        'connect',
        new_callable=AsyncMock,
        side_effect=mock_connect
    ):
        await scenario_tools.add_target_mcp(
            name='Prometheus',
            url='http://localhost:9090/mcp',
            scenario_id=scenario_id
        )
    
    # 有目标 MCP 但没有角色，仍然不 ready
    status2 = scenario_tools.get_scenario_status(scenario_id=scenario_id)
    assert status2['ready'] is False
    
    # 添加角色
    from fakemcp.tools.actor_tools import ActorTools
    actor_tools = ActorTools(scenario_tools.db)
    actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='测试服务器'
    )
    
    # 现在应该 ready
    status3 = scenario_tools.get_scenario_status(scenario_id=scenario_id)
    assert status3['ready'] is True
    assert status3['actors'] == 1


def test_get_scenario_status_not_found(scenario_tools):
    """测试获取不存在的场景状态"""
    result = scenario_tools.get_scenario_status(scenario_id='nonexistent')
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'ScenarioNotFoundError'


def test_get_tool_definitions(scenario_tools):
    """测试获取工具定义"""
    definitions = scenario_tools.get_tool_definitions()
    
    assert len(definitions) == 3
    
    # 验证工具名称
    tool_names = [d['name'] for d in definitions]
    assert 'set_scenario' in tool_names
    assert 'add_target_mcp' in tool_names
    assert 'get_scenario_status' in tool_names
    
    # 验证每个工具都有必要的字段
    for tool_def in definitions:
        assert 'name' in tool_def
        assert 'description' in tool_def
        assert 'inputSchema' in tool_def
        assert 'type' in tool_def['inputSchema']
        assert 'properties' in tool_def['inputSchema']


@pytest.mark.asyncio
async def test_target_id_generation(scenario_tools):
    """测试目标 MCP ID 生成"""
    mock_target_mcp = MagicMock()
    mock_target_mcp.id = 'cloud_monitoring'
    mock_target_mcp.name = 'Cloud Monitoring'
    mock_target_mcp.url = 'http://localhost:8080/mcp'
    mock_target_mcp.schema = {'tools': []}
    mock_target_mcp.actor_fields = []
    mock_target_mcp.connected = True
    
    with patch.object(
        scenario_tools.target_mcp_analyzer,
        'connect',
        new_callable=AsyncMock,
        return_value=mock_target_mcp
    ):
        result = await scenario_tools.add_target_mcp(
            name='Cloud Monitoring',
            url='http://localhost:8080/mcp'
        )
    
    # 验证 ID 生成规则：小写、空格和连字符转为下划线
    assert result['targetId'] == 'cloud_monitoring'


@pytest.mark.asyncio
async def test_close_resources(scenario_tools):
    """测试关闭资源"""
    # Mock the close method
    with patch.object(
        scenario_tools.target_mcp_analyzer,
        'close',
        new_callable=AsyncMock
    ) as mock_close:
        await scenario_tools.close()
        mock_close.assert_called_once()
