"""
Tests for Actor Tools
"""

import pytest
from fakemcp.database import Database
from fakemcp.tools.actor_tools import ActorTools


@pytest.fixture
def database():
    """Create an in-memory database for testing"""
    db = Database(':memory:')
    return db


@pytest.fixture
def actor_tools(database):
    """Create ActorTools instance"""
    return ActorTools(database)


def test_add_actor_config(actor_tools):
    """测试添加角色配置"""
    result = actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='内存持续增长，从 2GB 增长到 8GB'
    )
    
    assert result['success'] is True
    assert result['actorKey'] == 'server_id:server-01'
    assert 'actor' in result
    assert result['actor']['actor_type'] == 'server_id'
    assert result['actor']['actor_id'] == 'server-01'
    assert result['actor']['description'] == '内存持续增长，从 2GB 增长到 8GB'


def test_add_actor_config_with_parent(actor_tools):
    """测试添加带父级关系的角色配置"""
    # 先添加父级角色
    parent_result = actor_tools.add_actor_config(
        actor_type='city',
        actor_id='深圳',
        description='天气很差'
    )
    assert parent_result['success'] is True
    
    # 添加子级角色
    child_result = actor_tools.add_actor_config(
        actor_type='district',
        actor_id='深圳南山区',
        description='空气质量差',
        parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
    )
    
    assert child_result['success'] is True
    assert child_result['actorKey'] == 'district:深圳南山区'
    assert 'inheritedFrom' in child_result
    assert child_result['inheritedFrom'] == 'city:深圳'
    assert child_result['actor']['parent_actor'] == {
        'actor_type': 'city',
        'actor_id': '深圳'
    }


def test_remove_actor_config(actor_tools):
    """测试删除角色配置"""
    # 先添加角色
    actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='测试服务器'
    )
    
    # 删除角色
    result = actor_tools.remove_actor_config(
        actor_type='server_id',
        actor_id='server-01'
    )
    
    assert result['success'] is True
    assert result['removed'] is True
    assert result['actorKey'] == 'server_id:server-01'


def test_remove_nonexistent_actor(actor_tools):
    """测试删除不存在的角色"""
    result = actor_tools.remove_actor_config(
        actor_type='server_id',
        actor_id='nonexistent'
    )
    
    assert result['success'] is True
    assert result['removed'] is False


def test_list_actors_empty(actor_tools):
    """测试列出空角色列表"""
    result = actor_tools.list_actors()
    
    assert 'actors' in result
    assert result['count'] == 0
    assert len(result['actors']) == 0


def test_list_actors(actor_tools):
    """测试列出角色列表"""
    # 添加多个角色
    actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='服务器1'
    )
    actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-02',
        description='服务器2'
    )
    actor_tools.add_actor_config(
        actor_type='user_id',
        actor_id='user-001',
        description='用户1'
    )
    
    # 列出所有角色
    result = actor_tools.list_actors()
    
    assert result['count'] == 3
    assert len(result['actors']) == 3
    
    # 验证角色信息
    actor_types = [a['actorType'] for a in result['actors']]
    assert 'server_id' in actor_types
    assert 'user_id' in actor_types


def test_list_actors_with_filter(actor_tools):
    """测试按类型过滤角色列表"""
    # 添加多个角色
    actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='服务器1'
    )
    actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-02',
        description='服务器2'
    )
    actor_tools.add_actor_config(
        actor_type='user_id',
        actor_id='user-001',
        description='用户1'
    )
    
    # 只列出 server_id 类型的角色
    result = actor_tools.list_actors(actor_type='server_id')
    
    assert result['count'] == 2
    assert all(a['actorType'] == 'server_id' for a in result['actors'])


def test_list_actors_with_hierarchy(actor_tools):
    """测试列出角色时包含层级信息"""
    # 添加父子角色
    actor_tools.add_actor_config(
        actor_type='city',
        actor_id='深圳',
        description='城市'
    )
    actor_tools.add_actor_config(
        actor_type='district',
        actor_id='深圳南山区',
        description='区域',
        parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
    )
    
    # 列出角色并包含层级信息
    result = actor_tools.list_actors(include_hierarchy=True)
    
    assert result['count'] == 2
    
    # 找到子角色并验证层级信息
    child_actor = next(
        a for a in result['actors']
        if a['actorId'] == '深圳南山区'
    )
    assert 'hierarchy' in child_actor
    assert child_actor['hierarchy'] == ['city:深圳', 'district:深圳南山区']


def test_get_actor_details(actor_tools):
    """测试获取角色详细信息"""
    # 添加角色
    actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='内存持续增长，从 2GB 增长到 8GB'
    )
    
    # 获取详细信息
    result = actor_tools.get_actor_details(
        actor_type='server_id',
        actor_id='server-01'
    )
    
    assert result['success'] is True
    assert 'actor' in result
    assert result['actor']['actorType'] == 'server_id'
    assert result['actor']['actorId'] == 'server-01'


def test_get_actor_details_not_found(actor_tools):
    """测试获取不存在的角色"""
    result = actor_tools.get_actor_details(
        actor_type='server_id',
        actor_id='nonexistent'
    )
    
    assert result['success'] is False
    assert 'error' in result
    assert result['error']['type'] == 'ActorNotFoundError'


def test_get_actor_details_with_inheritance(actor_tools):
    """测试获取角色详细信息（包含继承）"""
    # 添加父子角色
    actor_tools.add_actor_config(
        actor_type='city',
        actor_id='深圳',
        description='天气很差'
    )
    actor_tools.add_actor_config(
        actor_type='district',
        actor_id='深圳南山区',
        description='空气质量差',
        parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
    )
    
    # 获取子角色详细信息（应用继承）
    result = actor_tools.get_actor_details(
        actor_type='district',
        actor_id='深圳南山区',
        with_inheritance=True
    )
    
    assert result['success'] is True
    assert 'hierarchy' in result
    assert result['hierarchy'] == ['city:深圳', 'district:深圳南山区']
    # 描述应该包含父级和子级的描述
    assert '天气很差' in result['actor']['description']
    assert '空气质量差' in result['actor']['description']


def test_get_tool_definitions(actor_tools):
    """测试获取工具定义"""
    definitions = actor_tools.get_tool_definitions()
    
    assert len(definitions) == 3
    
    # 验证工具名称
    tool_names = [d['name'] for d in definitions]
    assert 'add_actor_config' in tool_names
    assert 'remove_actor_config' in tool_names
    assert 'list_actors' in tool_names
    
    # 验证每个工具都有必要的字段
    for tool_def in definitions:
        assert 'name' in tool_def
        assert 'description' in tool_def
        assert 'inputSchema' in tool_def
        assert 'type' in tool_def['inputSchema']
        assert 'properties' in tool_def['inputSchema']


def test_update_existing_actor(actor_tools):
    """测试更新已存在的角色（追加配置）"""
    # 第一次添加
    result1 = actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='初始描述'
    )
    assert result1['success'] is True
    
    # 第二次添加（应该更新而不是创建新的）
    result2 = actor_tools.add_actor_config(
        actor_type='server_id',
        actor_id='server-01',
        description='更新后的描述'
    )
    assert result2['success'] is True
    
    # 验证只有一个角色
    list_result = actor_tools.list_actors(actor_type='server_id')
    assert list_result['count'] == 1
    assert list_result['actors'][0]['description'] == '更新后的描述'
