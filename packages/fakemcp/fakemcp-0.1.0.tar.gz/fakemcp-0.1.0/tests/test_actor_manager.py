"""
Tests for Actor Manager
"""

import pytest
from fakemcp.actor_manager import ActorManager
from fakemcp.database import Database
from fakemcp.models import Actor


@pytest.fixture
def db():
    """Create a test database"""
    database = Database(":memory:")
    yield database
    database.close()


@pytest.fixture
def actor_manager(db):
    """Create an actor manager instance"""
    return ActorManager(db)


class TestActorBasicOperations:
    """Test basic actor CRUD operations"""

    def test_add_actor(self, actor_manager):
        """Test adding a new actor"""
        actor = actor_manager.add_actor(
            actor_type='server_id',
            actor_id='server-01',
            description='内存持续增长，从 2GB 增长到 8GB'
        )
        
        assert actor.actor_type == 'server_id'
        assert actor.actor_id == 'server-01'
        assert actor.description == '内存持续增长，从 2GB 增长到 8GB'
        assert isinstance(actor.state, dict)
        assert isinstance(actor.metadata, dict)

    def test_add_actor_with_state(self, actor_manager):
        """Test adding actor with initial state"""
        state = {'memory_usage': 2048, 'cpu_usage': 50}
        actor = actor_manager.add_actor(
            actor_type='server_id',
            actor_id='server-02',
            description='正常运行',
            state=state
        )
        
        assert actor.state == state

    def test_add_actor_with_parent(self, actor_manager):
        """Test adding actor with parent relationship"""
        # Add parent
        parent = actor_manager.add_actor(
            actor_type='city',
            actor_id='深圳',
            description='天气很差'
        )
        
        # Add child
        child = actor_manager.add_actor(
            actor_type='district',
            actor_id='深圳南山区',
            description='继承深圳的天气',
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        
        assert child.parent_actor == {'actor_type': 'city', 'actor_id': '深圳'}

    def test_get_actor(self, actor_manager):
        """Test retrieving an actor"""
        actor_manager.add_actor(
            actor_type='server_id',
            actor_id='server-01',
            description='测试服务器'
        )
        
        retrieved = actor_manager.get_actor('server_id', 'server-01')
        assert retrieved is not None
        assert retrieved.actor_id == 'server-01'

    def test_get_nonexistent_actor(self, actor_manager):
        """Test retrieving non-existent actor"""
        result = actor_manager.get_actor('server_id', 'nonexistent')
        assert result is None

    def test_remove_actor(self, actor_manager):
        """Test removing an actor"""
        actor_manager.add_actor(
            actor_type='server_id',
            actor_id='server-01',
            description='测试服务器'
        )
        
        result = actor_manager.remove_actor('server_id', 'server-01')
        assert result is True
        
        # Verify it's gone
        retrieved = actor_manager.get_actor('server_id', 'server-01')
        assert retrieved is None

    def test_remove_nonexistent_actor(self, actor_manager):
        """Test removing non-existent actor"""
        result = actor_manager.remove_actor('server_id', 'nonexistent')
        assert result is False

    def test_list_actors(self, actor_manager):
        """Test listing all actors"""
        actor_manager.add_actor('server_id', 'server-01', '服务器1')
        actor_manager.add_actor('server_id', 'server-02', '服务器2')
        actor_manager.add_actor('city', '深圳', '城市')
        
        actors = actor_manager.list_actors()
        assert len(actors) == 3

    def test_list_actors_by_type(self, actor_manager):
        """Test listing actors filtered by type"""
        actor_manager.add_actor('server_id', 'server-01', '服务器1')
        actor_manager.add_actor('server_id', 'server-02', '服务器2')
        actor_manager.add_actor('city', '深圳', '城市')
        
        servers = actor_manager.list_actors(actor_type='server_id')
        assert len(servers) == 2
        assert all(a.actor_type == 'server_id' for a in servers)


class TestActorHierarchy:
    """Test actor hierarchical relationships"""

    def test_resolve_single_actor_hierarchy(self, actor_manager):
        """Test resolving hierarchy for actor without parent"""
        actor_manager.add_actor('city', '深圳', '城市')
        
        hierarchy = actor_manager.resolve_actor_hierarchy('city', '深圳')
        assert len(hierarchy) == 1
        assert hierarchy[0].actor_id == '深圳'

    def test_resolve_two_level_hierarchy(self, actor_manager):
        """Test resolving two-level hierarchy"""
        # Add parent
        actor_manager.add_actor('city', '深圳', '城市')
        
        # Add child
        actor_manager.add_actor(
            'district',
            '深圳南山区',
            '区域',
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        
        hierarchy = actor_manager.resolve_actor_hierarchy('district', '深圳南山区')
        assert len(hierarchy) == 2
        assert hierarchy[0].actor_id == '深圳'  # Parent first
        assert hierarchy[1].actor_id == '深圳南山区'  # Child second

    def test_resolve_three_level_hierarchy(self, actor_manager):
        """Test resolving three-level hierarchy"""
        # Add grandparent
        actor_manager.add_actor('country', '中国', '国家')
        
        # Add parent
        actor_manager.add_actor(
            'city',
            '深圳',
            '城市',
            parent_actor={'actor_type': 'country', 'actor_id': '中国'}
        )
        
        # Add child
        actor_manager.add_actor(
            'district',
            '深圳南山区',
            '区域',
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        
        hierarchy = actor_manager.resolve_actor_hierarchy('district', '深圳南山区')
        assert len(hierarchy) == 3
        assert hierarchy[0].actor_id == '中国'
        assert hierarchy[1].actor_id == '深圳'
        assert hierarchy[2].actor_id == '深圳南山区'

    def test_resolve_nonexistent_actor_hierarchy(self, actor_manager):
        """Test resolving hierarchy for non-existent actor"""
        hierarchy = actor_manager.resolve_actor_hierarchy('city', 'nonexistent')
        assert len(hierarchy) == 0


class TestActorInheritance:
    """Test actor inheritance logic"""

    def test_get_actor_with_inheritance_no_parent(self, actor_manager):
        """Test inheritance for actor without parent"""
        actor_manager.add_actor(
            'city',
            '深圳',
            '天气很差',
            state={'temperature': 35},
            metadata={'status': 'bad'}
        )
        
        merged = actor_manager.get_actor_with_inheritance('city', '深圳')
        assert merged is not None
        assert merged.state == {'temperature': 35}
        assert merged.metadata['status'] == 'bad'

    def test_get_actor_with_inheritance_from_parent(self, actor_manager):
        """Test child inherits from parent"""
        # Add parent with state
        actor_manager.add_actor(
            'city',
            '深圳',
            '天气很差',
            state={'temperature': 35, 'humidity': 80},
            metadata={'status': 'bad'}
        )
        
        # Add child with partial state
        actor_manager.add_actor(
            'district',
            '深圳南山区',
            '区域特征',
            state={'pollution': 'high'},
            metadata={'population': 'dense'},
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        
        merged = actor_manager.get_actor_with_inheritance('district', '深圳南山区')
        assert merged is not None
        # Child should have both parent and own state
        assert merged.state['temperature'] == 35
        assert merged.state['humidity'] == 80
        assert merged.state['pollution'] == 'high'
        # Child should have both parent and own metadata
        assert merged.metadata['status'] == 'bad'
        assert merged.metadata['population'] == 'dense'

    def test_get_actor_with_inheritance_override(self, actor_manager):
        """Test child overrides parent values"""
        # Add parent
        actor_manager.add_actor(
            'city',
            '深圳',
            '天气很差',
            state={'temperature': 35},
            metadata={'status': 'bad'}
        )
        
        # Add child with overriding values
        actor_manager.add_actor(
            'district',
            '深圳南山区',
            '区域天气更好',
            state={'temperature': 28},  # Override
            metadata={'status': 'good'},  # Override
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        
        merged = actor_manager.get_actor_with_inheritance('district', '深圳南山区')
        assert merged is not None
        # Child values should override parent
        assert merged.state['temperature'] == 28
        assert merged.metadata['status'] == 'good'

    def test_get_actor_with_inheritance_description_merge(self, actor_manager):
        """Test descriptions are merged in hierarchy"""
        actor_manager.add_actor('city', '深圳', '天气很差')
        actor_manager.add_actor(
            'district',
            '深圳南山区',
            '科技园区',
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        
        merged = actor_manager.get_actor_with_inheritance('district', '深圳南山区')
        assert merged is not None
        assert '天气很差' in merged.description
        assert '科技园区' in merged.description


class TestActorExtraction:
    """Test actor extraction from descriptions"""

    def test_extract_server_ids(self, actor_manager):
        """Test extracting server IDs"""
        description = "server-01 和 server-02 出现内存泄露"
        actors = actor_manager.extract_actors_from_description(description)
        
        server_actors = [a for a in actors if a['actor_type'] == 'server_id']
        assert len(server_actors) == 2
        assert any(a['actor_id'] == 'server-01' for a in server_actors)
        assert any(a['actor_id'] == 'server-02' for a in server_actors)

    def test_extract_user_ids(self, actor_manager):
        """Test extracting user IDs"""
        description = "user-001 和 user_123 的行为异常"
        actors = actor_manager.extract_actors_from_description(description)
        
        user_actors = [a for a in actors if a['actor_type'] == 'user_id']
        assert len(user_actors) == 2

    def test_extract_chinese_cities(self, actor_manager):
        """Test extracting Chinese city names"""
        description = "深圳和北京的天气都很差"
        actors = actor_manager.extract_actors_from_description(description)
        
        city_actors = [a for a in actors if a['actor_type'] == 'city']
        assert len(city_actors) == 2
        assert any(a['actor_id'] == '深圳' for a in city_actors)
        assert any(a['actor_id'] == '北京' for a in city_actors)

    def test_extract_districts(self, actor_manager):
        """Test extracting city districts"""
        description = "深圳南山区的天气"
        actors = actor_manager.extract_actors_from_description(description)
        
        district_actors = [a for a in actors if a['actor_type'] == 'district']
        assert len(district_actors) == 1
        assert district_actors[0]['actor_id'] == '深圳南山区'
        assert district_actors[0]['parent_city'] == '深圳'

    def test_extract_database_ids(self, actor_manager):
        """Test extracting database IDs"""
        description = "database-01 和 mysql-prod 连接失败"
        actors = actor_manager.extract_actors_from_description(description)
        
        db_actors = [a for a in actors if a['actor_type'] == 'database_id']
        assert len(db_actors) == 2

    def test_extract_mixed_actors(self, actor_manager):
        """Test extracting multiple types of actors"""
        description = "server-01 在深圳，user-001 访问 database-01"
        actors = actor_manager.extract_actors_from_description(description)
        
        assert len(actors) >= 3
        actor_types = {a['actor_type'] for a in actors}
        assert 'server_id' in actor_types
        assert 'city' in actor_types
        assert 'user_id' in actor_types
        assert 'database_id' in actor_types

    def test_extract_no_duplicates(self, actor_manager):
        """Test that extraction removes duplicates"""
        description = "server-01 和 server-01 和 server-01"
        actors = actor_manager.extract_actors_from_description(description)
        
        server_actors = [a for a in actors if a['actor_type'] == 'server_id']
        assert len(server_actors) == 1


class TestActorCreationFromExtraction:
    """Test creating actors from extracted information"""

    def test_create_actors_from_extraction(self, actor_manager):
        """Test creating actors from extraction results"""
        extracted = [
            {'actor_type': 'server_id', 'actor_id': 'server-01'},
            {'actor_type': 'server_id', 'actor_id': 'server-02'}
        ]
        
        created = actor_manager.create_actors_from_extraction(
            extracted,
            default_description='从场景描述中提取'
        )
        
        assert len(created) == 2
        assert all(isinstance(a, Actor) for a in created)
        
        # Verify they're in database
        actor1 = actor_manager.get_actor('server_id', 'server-01')
        assert actor1 is not None

    def test_create_actors_with_parent_relationship(self, actor_manager):
        """Test creating actors with parent relationships"""
        # First create parent
        actor_manager.add_actor('city', '深圳', '城市')
        
        extracted = [
            {
                'actor_type': 'district',
                'actor_id': '深圳南山区',
                'parent_city': '深圳'
            }
        ]
        
        created = actor_manager.create_actors_from_extraction(extracted)
        assert len(created) == 1
        assert created[0].parent_actor == {'actor_type': 'city', 'actor_id': '深圳'}


class TestMetadataExtraction:
    """Test metadata extraction from descriptions"""

    def test_extract_memory_values(self, actor_manager):
        """Test extracting memory values"""
        actor = actor_manager.add_actor(
            'server_id',
            'server-01',
            '内存从 2GB 增长到 8GB'
        )
        
        assert 'memory' in actor.metadata
        assert len(actor.metadata['memory']) == 2

    def test_extract_time_values(self, actor_manager):
        """Test extracting time values"""
        actor = actor_manager.add_actor(
            'server_id',
            'server-01',
            '响应时间从 100ms 增加到 2000ms'
        )
        
        assert 'time' in actor.metadata
        assert len(actor.metadata['time']) == 2

    def test_extract_percentage_values(self, actor_manager):
        """Test extracting percentage values"""
        actor = actor_manager.add_actor(
            'server_id',
            'server-01',
            'CPU 使用率达到 95%'
        )
        
        assert 'percentage' in actor.metadata
        assert actor.metadata['percentage'][0]['value'] == 95

    def test_extract_status_keywords(self, actor_manager):
        """Test extracting status keywords"""
        test_cases = [
            ('服务器正常运行', 'normal'),
            ('出现警告', 'warning'),
            ('发生错误', 'error'),
            ('天气很差', 'bad'),
            ('状态良好', 'good')
        ]
        
        for description, expected_status in test_cases:
            actor = actor_manager.add_actor(
                'test',
                f'test-{expected_status}',
                description
            )
            assert actor.metadata.get('status') == expected_status

    def test_extract_trend_keywords(self, actor_manager):
        """Test extracting trend keywords"""
        test_cases = [
            ('内存持续增长', 'increasing'),
            ('CPU 使用率下降', 'decreasing'),
            ('保持稳定', 'stable'),
            ('数值波动', 'fluctuating')
        ]
        
        for description, expected_trend in test_cases:
            actor = actor_manager.add_actor(
                'test',
                f'test-{expected_trend}',
                description
            )
            assert actor.metadata.get('trend') == expected_trend


class TestActorStateUpdate:
    """Test actor state updates"""

    def test_update_actor_state(self, actor_manager):
        """Test updating actor state"""
        actor_manager.add_actor(
            'server_id',
            'server-01',
            '测试',
            state={'memory': 2048}
        )
        
        updated = actor_manager.update_actor_state(
            'server_id',
            'server-01',
            {'memory': 4096, 'cpu': 50}
        )
        
        assert updated is not None
        assert updated.state['memory'] == 4096
        assert updated.state['cpu'] == 50

    def test_update_nonexistent_actor_state(self, actor_manager):
        """Test updating state of non-existent actor"""
        result = actor_manager.update_actor_state(
            'server_id',
            'nonexistent',
            {'memory': 4096}
        )
        assert result is None


class TestFindChildActors:
    """Test finding child actors"""

    def test_find_child_actors(self, actor_manager):
        """Test finding children of a parent actor"""
        # Add parent
        actor_manager.add_actor('city', '深圳', '城市')
        
        # Add children
        actor_manager.add_actor(
            'district',
            '深圳南山区',
            '区域1',
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        actor_manager.add_actor(
            'district',
            '深圳福田区',
            '区域2',
            parent_actor={'actor_type': 'city', 'actor_id': '深圳'}
        )
        
        # Add unrelated actor
        actor_manager.add_actor('city', '北京', '城市')
        
        children = actor_manager.find_child_actors('city', '深圳')
        assert len(children) == 2
        assert all(c.parent_actor['actor_id'] == '深圳' for c in children)

    def test_find_child_actors_no_children(self, actor_manager):
        """Test finding children when there are none"""
        actor_manager.add_actor('city', '深圳', '城市')
        
        children = actor_manager.find_child_actors('city', '深圳')
        assert len(children) == 0
