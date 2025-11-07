"""
Tests for Guide Tool implementation
"""

import pytest
from fakemcp.database import Database
from fakemcp.tools.guide_tool import GuideTools
from fakemcp.workflow_guide import WorkflowGuide


@pytest.fixture
def database():
    """创建测试数据库"""
    db = Database(':memory:')
    yield db


@pytest.fixture
def guide_tools(database):
    """创建 GuideTools 实例"""
    return GuideTools(database)


@pytest.mark.asyncio
async def test_guide_tool_initialization(guide_tools):
    """测试 guide 工具初始化"""
    assert guide_tools is not None
    assert isinstance(guide_tools.workflow_guide, WorkflowGuide)


@pytest.mark.asyncio
async def test_guide_start_action(guide_tools):
    """测试 guide 工具的 start 操作"""
    result = await guide_tools.guide(action='start')
    
    assert result['success'] is True
    assert result['stage'] == 'init'
    assert 'prompt' in result
    assert 'nextActions' in result
    assert 'progress' in result
    assert result['progress'] == 0
    assert '场景' in result['prompt']
    assert 'set_scenario' in result['nextActions']


@pytest.mark.asyncio
async def test_guide_next_action(guide_tools):
    """测试 guide 工具的 next 操作"""
    # 先启动工作流
    await guide_tools.guide(action='start')
    
    # 获取下一步引导
    result = await guide_tools.guide(action='next')
    
    assert result['success'] is True
    assert result['stage'] == 'init'
    assert 'prompt' in result
    assert 'nextActions' in result
    assert 'progress' in result


@pytest.mark.asyncio
async def test_guide_status_action(guide_tools):
    """测试 guide 工具的 status 操作"""
    # 先启动工作流
    await guide_tools.guide(action='start')
    
    # 查询状态
    result = await guide_tools.guide(action='status')
    
    assert result['success'] is True
    assert result['stage'] == 'init'
    assert 'prompt' in result
    assert 'data' in result
    assert 'history' in result
    assert isinstance(result['history'], list)


@pytest.mark.asyncio
async def test_guide_reset_action(guide_tools):
    """测试 guide 工具的 reset 操作"""
    # 先启动工作流
    await guide_tools.guide(action='start')
    
    # 推进到下一阶段
    guide_tools.workflow_guide.advance_stage()
    
    # 重置工作流
    result = await guide_tools.guide(action='reset')
    
    assert result['success'] is True
    assert result['stage'] == 'init'
    assert result['progress'] == 0


@pytest.mark.asyncio
async def test_guide_invalid_action(guide_tools):
    """测试 guide 工具的无效操作"""
    result = await guide_tools.guide(action='invalid_action')
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'InvalidActionError'
    assert 'suggestions' in result['error']


@pytest.mark.asyncio
async def test_guide_default_action(guide_tools):
    """测试 guide 工具的默认操作（next）"""
    result = await guide_tools.guide()
    
    assert result['success'] is True
    assert 'stage' in result
    assert 'prompt' in result


@pytest.mark.asyncio
async def test_guide_workflow_progression(guide_tools):
    """测试 guide 工具在工作流推进中的表现"""
    # 启动工作流
    result1 = await guide_tools.guide(action='start')
    assert result1['stage'] == 'init'
    progress1 = result1['progress']
    
    # 推进到下一阶段
    guide_tools.workflow_guide.advance_stage()
    
    # 获取新阶段的引导
    result2 = await guide_tools.guide(action='next')
    assert result2['stage'] == 'target_collection'
    progress2 = result2['progress']
    
    # 进度应该增加
    assert progress2 > progress1


@pytest.mark.asyncio
async def test_guide_all_stages(guide_tools):
    """测试 guide 工具在所有工作流阶段的表现"""
    stages = [
        'init',
        'target_collection',
        'actor_analysis',
        'plot_deepening',
        'scenario_creation',
        'data_generation',
        'validation',
        'correction',
        'completed'
    ]
    
    # 启动工作流
    await guide_tools.guide(action='start')
    
    for expected_stage in stages:
        result = await guide_tools.guide(action='next')
        assert result['success'] is True
        assert result['stage'] == expected_stage
        assert 'prompt' in result
        assert 'nextActions' in result
        assert isinstance(result['nextActions'], list)
        
        # 推进到下一阶段（除了最后一个）
        if expected_stage != 'completed':
            guide_tools.workflow_guide.advance_stage()


@pytest.mark.asyncio
async def test_guide_tool_definitions(guide_tools):
    """测试 guide 工具定义"""
    definitions = guide_tools.get_tool_definitions()
    
    assert len(definitions) == 1
    
    guide_def = definitions[0]
    assert guide_def['name'] == 'guide'
    assert 'description' in guide_def
    assert 'inputSchema' in guide_def
    
    # 验证 schema
    schema = guide_def['inputSchema']
    assert schema['type'] == 'object'
    assert 'properties' in schema
    assert 'action' in schema['properties']
    
    # 验证 action 参数
    action_prop = schema['properties']['action']
    assert action_prop['type'] == 'string'
    assert 'enum' in action_prop
    assert set(action_prop['enum']) == {'start', 'next', 'status', 'reset'}


@pytest.mark.asyncio
async def test_guide_with_workflow_data(guide_tools):
    """测试 guide 工具在有工作流数据时的表现"""
    # 启动工作流
    await guide_tools.guide(action='start')
    
    # 添加一些工作流数据
    guide_tools.workflow_guide.update_data({
        'scenario_description': '内存泄露场景',
        'target_mcps': ['prometheus', 'cloudmonitoring'],
        'actors': ['server-01', 'server-02']
    })
    
    # 推进到 actor_analysis 阶段
    guide_tools.workflow_guide.advance_stage()  # target_collection
    guide_tools.workflow_guide.advance_stage()  # actor_analysis
    
    # 获取引导
    result = await guide_tools.guide(action='next')
    
    assert result['success'] is True
    assert result['stage'] == 'actor_analysis'
    assert '内存泄露场景' in result['prompt']


@pytest.mark.asyncio
async def test_guide_progress_calculation(guide_tools):
    """测试 guide 工具的进度计算"""
    # 启动工作流
    result = await guide_tools.guide(action='start')
    assert result['progress'] == 0
    
    # 推进到中间阶段
    for _ in range(4):  # 推进到 scenario_creation
        guide_tools.workflow_guide.advance_stage()
    
    result = await guide_tools.guide(action='next')
    assert 0 < result['progress'] < 100
    
    # 推进到完成阶段
    while guide_tools.workflow_guide.get_current_state().stage != 'completed':
        guide_tools.workflow_guide.advance_stage()
    
    result = await guide_tools.guide(action='next')
    assert result['progress'] == 100
