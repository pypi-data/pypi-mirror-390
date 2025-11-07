"""
Tests for Plot Tools
"""

import pytest
from fakemcp.database import Database
from fakemcp.models import Scenario
from fakemcp.tools.plot_tools import PlotTools
from fakemcp.scenario_manager import ScenarioManager
from fakemcp.actor_manager import ActorManager


@pytest.fixture
def database():
    """Create an in-memory database for testing"""
    db = Database(':memory:')
    return db


@pytest.fixture
def plot_tools(database):
    """Create PlotTools instance"""
    return PlotTools(database)


@pytest.fixture
def scenario_manager(database):
    """Create ScenarioManager instance"""
    return ScenarioManager(database)


@pytest.fixture
def actor_manager(database):
    """Create ActorManager instance"""
    return ActorManager(database)


@pytest.fixture
def sample_scenario(scenario_manager):
    """Create a sample scenario for testing"""
    scenario = scenario_manager.create_scenario(
        description="模拟内存泄露场景",
        target_mcps=["prometheus", "cloudmonitoring", "logging"]
    )
    return scenario


def test_add_causality_relation(plot_tools):
    """测试添加因果关系"""
    result = plot_tools.add_causality_relation(
        cause_actor="server-02",
        cause_event="错误请求增加",
        effect_actor="server-01",
        effect_event="内存泄露",
        time_delay=300,
        strength=0.9
    )
    
    assert result['success'] is True
    assert 'relationId' in result
    assert result['plotUpdated'] is True
    assert result['causeActor'] == "server-02"
    assert result['causeEvent'] == "错误请求增加"
    assert result['effectActor'] == "server-01"
    assert result['effectEvent'] == "内存泄露"
    assert result['timeDelay'] == 300
    assert result['strength'] == 0.9


def test_add_causality_relation_default_values(plot_tools):
    """测试添加因果关系（使用默认值）"""
    result = plot_tools.add_causality_relation(
        cause_actor="server-02",
        cause_event="错误请求",
        effect_actor="server-01",
        effect_event="内存泄露"
    )
    
    assert result['success'] is True
    assert result['timeDelay'] == 0
    assert result['strength'] == 1.0


def test_build_plot_graph_empty(plot_tools):
    """测试构建空剧情图"""
    result = plot_tools.build_plot_graph()
    
    assert result['success'] is True
    assert 'plotGraph' in result
    assert 'timeline' in result
    assert result['nodeCount'] == 0
    assert result['edgeCount'] == 0


def test_build_plot_graph_with_relations(plot_tools):
    """测试构建包含因果关系的剧情图"""
    # 添加因果关系
    plot_tools.add_causality_relation(
        cause_actor="server-02",
        cause_event="错误请求增加",
        effect_actor="server-01",
        effect_event="内存泄露",
        time_delay=300
    )
    
    plot_tools.add_causality_relation(
        cause_actor="server-01",
        cause_event="内存泄露",
        effect_actor="server-01",
        effect_event="响应变慢",
        time_delay=600
    )
    
    # 构建剧情图
    result = plot_tools.build_plot_graph()
    
    assert result['success'] is True
    assert result['nodeCount'] == 3  # server-02:错误请求, server-01:内存泄露, server-01:响应变慢
    assert result['edgeCount'] == 2
    
    # 验证时间线
    timeline = result['timeline']
    assert len(timeline) >= 2
    assert timeline[0]['timestamp'] == 0
    assert timeline[1]['timestamp'] == 300


def test_validate_plot_consistency_empty(plot_tools):
    """测试验证空剧情图的一致性"""
    result = plot_tools.validate_plot_consistency()
    
    assert result['success'] is True
    assert result['consistent'] is True
    assert len(result['issues']) == 0
    assert len(result['suggestions']) == 0


def test_validate_plot_consistency_valid(plot_tools, actor_manager):
    """测试验证有效剧情图的一致性"""
    # 添加角色
    actor_manager.add_actor(
        actor_type="server_id",
        actor_id="server-01",
        description="服务器1"
    )
    actor_manager.add_actor(
        actor_type="server_id",
        actor_id="server-02",
        description="服务器2"
    )
    
    # 添加因果关系
    plot_tools.add_causality_relation(
        cause_actor="server-02",
        cause_event="错误请求",
        effect_actor="server-01",
        effect_event="内存泄露",
        time_delay=300
    )
    
    # 验证一致性
    result = plot_tools.validate_plot_consistency()
    
    assert result['success'] is True
    assert result['consistent'] is True
    assert len(result['issues']) == 0


def test_validate_plot_consistency_circular_dependency(plot_tools):
    """测试检测循环依赖"""
    # 创建循环依赖: A -> B -> A
    plot_tools.add_causality_relation(
        cause_actor="server-01",
        cause_event="event-a",
        effect_actor="server-02",
        effect_event="event-b"
    )
    
    plot_tools.add_causality_relation(
        cause_actor="server-02",
        cause_event="event-b",
        effect_actor="server-01",
        effect_event="event-a"
    )
    
    # 验证一致性
    result = plot_tools.validate_plot_consistency()
    
    assert result['success'] is True
    assert result['consistent'] is False
    assert len(result['issues']) > 0
    
    # 检查是否检测到循环依赖
    circular_issues = [
        issue for issue in result['issues']
        if issue['type'] == 'circular_dependency'
    ]
    assert len(circular_issues) > 0


def test_validate_plot_consistency_missing_actors(plot_tools):
    """测试检测缺失的角色"""
    # 添加因果关系但不添加角色
    plot_tools.add_causality_relation(
        cause_actor="nonexistent-actor",
        cause_event="event",
        effect_actor="server-01",
        effect_event="result"
    )
    
    # 验证一致性
    result = plot_tools.validate_plot_consistency()
    
    assert result['success'] is True
    assert result['consistent'] is False
    
    # 检查是否检测到缺失的角色
    missing_actor_issues = [
        issue for issue in result['issues']
        if issue['type'] == 'missing_actor'
    ]
    assert len(missing_actor_issues) > 0


def test_request_plot_expansion_no_scenario(plot_tools):
    """测试在没有场景时请求剧情扩展"""
    result = plot_tools.request_plot_expansion(
        actor_id="server-01",
        event="内存泄露"
    )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'NoScenarioError'


def test_request_plot_expansion_with_scenario(plot_tools, sample_scenario, actor_manager):
    """测试请求剧情扩展"""
    # 添加一些角色
    actor_manager.add_actor(
        actor_type="server_id",
        actor_id="server-01",
        description="服务器1"
    )
    actor_manager.add_actor(
        actor_type="server_id",
        actor_id="server-02",
        description="服务器2"
    )
    
    # 请求剧情扩展
    result = plot_tools.request_plot_expansion(
        actor_id="server-01",
        event="内存泄露",
        scenario_id=sample_scenario.id
    )
    
    assert result['success'] is True
    assert 'promptForAI' in result
    assert 'currentActors' in result
    assert 'targetMcps' in result
    assert 'exampleFormat' in result
    
    # 验证提示词包含关键信息
    prompt = result['promptForAI']
    assert "server-01" in prompt
    assert "内存泄露" in prompt
    assert "模拟内存泄露场景" in prompt
    
    # 验证当前角色列表
    assert "server-01" in result['currentActors']
    assert "server-02" in result['currentActors']
    
    # 验证目标 MCP 列表
    assert "prometheus" in result['targetMcps']
    assert "cloudmonitoring" in result['targetMcps']


def test_request_plot_expansion_with_existing_relations(plot_tools, sample_scenario, actor_manager):
    """测试请求剧情扩展（已有因果关系）"""
    # 添加角色
    actor_manager.add_actor(
        actor_type="server_id",
        actor_id="server-01",
        description="服务器1"
    )
    
    # 添加因果关系
    plot_tools.add_causality_relation(
        cause_actor="server-02",
        cause_event="错误请求",
        effect_actor="server-01",
        effect_event="内存泄露",
        time_delay=300
    )
    
    # 请求剧情扩展
    result = plot_tools.request_plot_expansion(
        actor_id="server-01",
        event="内存泄露",
        scenario_id=sample_scenario.id
    )
    
    assert result['success'] is True
    
    # 提示词应该包含已有的因果关系
    prompt = result['promptForAI']
    assert "已有的因果关系" in prompt
    assert "server-02" in prompt
    assert "错误请求" in prompt


def test_get_tool_definitions(plot_tools):
    """测试获取工具定义"""
    definitions = plot_tools.get_tool_definitions()
    
    assert len(definitions) == 4
    
    # 验证工具名称
    tool_names = [d['name'] for d in definitions]
    assert 'request_plot_expansion' in tool_names
    assert 'add_causality_relation' in tool_names
    assert 'build_plot_graph' in tool_names
    assert 'validate_plot_consistency' in tool_names
    
    # 验证每个工具都有必要的字段
    for tool_def in definitions:
        assert 'name' in tool_def
        assert 'description' in tool_def
        assert 'inputSchema' in tool_def
        assert 'type' in tool_def['inputSchema']
        assert 'properties' in tool_def['inputSchema']


def test_complex_plot_graph(plot_tools, actor_manager):
    """测试复杂剧情图（多层因果链）"""
    # 添加角色
    for i in range(1, 5):
        actor_manager.add_actor(
            actor_type="server_id",
            actor_id=f"server-0{i}",
            description=f"服务器{i}"
        )
    
    # 创建因果链: server-01 -> server-02 -> server-03 -> server-04
    plot_tools.add_causality_relation(
        cause_actor="server-01",
        cause_event="高负载",
        effect_actor="server-02",
        effect_event="连接超时",
        time_delay=60
    )
    
    plot_tools.add_causality_relation(
        cause_actor="server-02",
        cause_event="连接超时",
        effect_actor="server-03",
        effect_event="请求失败",
        time_delay=120
    )
    
    plot_tools.add_causality_relation(
        cause_actor="server-03",
        cause_event="请求失败",
        effect_actor="server-04",
        effect_event="服务降级",
        time_delay=180
    )
    
    # 构建剧情图
    result = plot_tools.build_plot_graph()
    
    assert result['success'] is True
    assert result['nodeCount'] == 4
    assert result['edgeCount'] == 3
    
    # 验证时间线
    timeline = result['timeline']
    assert len(timeline) == 4
    assert timeline[0]['timestamp'] == 0
    assert timeline[1]['timestamp'] == 60
    assert timeline[2]['timestamp'] == 180
    assert timeline[3]['timestamp'] == 360
    
    # 验证一致性
    validation = plot_tools.validate_plot_consistency()
    assert validation['consistent'] is True
