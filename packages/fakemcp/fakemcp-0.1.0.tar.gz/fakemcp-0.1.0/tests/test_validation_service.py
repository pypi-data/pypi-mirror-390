"""
Tests for ValidationService
"""

import pytest
from datetime import datetime, timedelta
from fakemcp.validation_service import ValidationService
from fakemcp.models import (
    CausalityRelation, Scenario, TargetMCP, Actor, PlotNode
)
from fakemcp.plot_manager import PlotGraph, PlotManager
from fakemcp.database import Database


@pytest.fixture
def db():
    """Create an in-memory database for testing"""
    return Database(":memory:")


@pytest.fixture
def plot_manager(db):
    """Create a PlotManager instance"""
    return PlotManager(db)


@pytest.fixture
def validation_service(plot_manager):
    """Create a ValidationService instance"""
    return ValidationService(plot_manager)


@pytest.fixture
def sample_scenario():
    """Create a sample scenario"""
    return Scenario(
        id="test-scenario",
        description="Memory leak scenario",
        target_mcps=["prometheus", "logging"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={}
    )


@pytest.fixture
def sample_target_mcp():
    """Create a sample target MCP"""
    return TargetMCP(
        id="prometheus",
        name="Prometheus",
        url="http://localhost:9090",
        config={},
        schema={
            'tools': [
                {
                    'name': 'query_metrics',
                    'outputSchema': {
                        'type': 'object',
                        'properties': {
                            'timestamp': {'type': 'string'},
                            'value': {'type': 'number'},
                            'labels': {'type': 'object'}
                        },
                        'required': ['timestamp', 'value']
                    }
                }
            ]
        },
        actor_fields=['instance'],
        example_data={},
        connected=True
    )


class TestSchemaValidation:
    """Test schema validation functionality"""
    
    def test_validate_schema_valid_data(self, validation_service):
        """Test schema validation with valid data"""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'number'}
            },
            'required': ['name']
        }
        
        data = {'name': 'John', 'age': 30}
        
        valid, errors = validation_service.validate_schema(data, schema)
        
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_schema_invalid_data(self, validation_service):
        """Test schema validation with invalid data"""
        schema = {
            'type': 'object',
            'properties': {
                'name': {'type': 'string'},
                'age': {'type': 'number'}
            },
            'required': ['name']
        }
        
        data = {'age': 'thirty'}  # Missing required field and wrong type
        
        valid, errors = validation_service.validate_schema(data, schema)
        
        assert valid is False
        assert len(errors) > 0
    
    def test_validate_schema_empty_schema(self, validation_service):
        """Test schema validation with empty schema"""
        data = {'any': 'data'}
        
        valid, errors = validation_service.validate_schema(data, {})
        
        assert valid is True
        assert len(errors) == 0


class TestMockDataValidation:
    """Test mock data validation functionality"""
    
    def test_validate_mock_data_valid(
        self, validation_service, sample_target_mcp, sample_scenario
    ):
        """Test validation of valid mock data"""
        mock_data = {
            'timestamp': '2024-01-01T00:00:00',
            'value': 42.5,
            'labels': {'instance': 'server-01'}
        }
        
        result = validation_service.validate_mock_data(
            mock_data, sample_target_mcp, 'query_metrics', sample_scenario
        )
        
        assert result['valid'] is True
        assert len(result['issues']) == 0
    
    def test_validate_mock_data_schema_mismatch(
        self, validation_service, sample_target_mcp, sample_scenario
    ):
        """Test validation with schema mismatch"""
        mock_data = {
            'timestamp': '2024-01-01T00:00:00',
            'value': 'not-a-number',  # Should be number
            'labels': {'instance': 'server-01'}
        }
        
        result = validation_service.validate_mock_data(
            mock_data, sample_target_mcp, 'query_metrics', sample_scenario
        )
        
        assert result['valid'] is False
        assert len(result['issues']) > 0
        assert len(result['suggestions']) > 0
    
    def test_validate_mock_data_invalid_timestamp(
        self, validation_service, sample_target_mcp, sample_scenario
    ):
        """Test validation with invalid timestamp"""
        mock_data = {
            'timestamp': 'invalid-timestamp',
            'value': 42.5,
            'labels': {'instance': 'server-01'}
        }
        
        result = validation_service.validate_mock_data(
            mock_data, sample_target_mcp, 'query_metrics', sample_scenario
        )
        
        assert result['valid'] is False
        assert any('timestamp' in issue.lower() for issue in result['issues'])
    
    def test_validate_mock_data_out_of_range(
        self, validation_service, sample_target_mcp, sample_scenario
    ):
        """Test validation with out-of-range values"""
        # Modify schema to include percentage field
        sample_target_mcp.schema['tools'][0]['outputSchema']['properties']['cpu_percent'] = {
            'type': 'number'
        }
        
        mock_data = {
            'timestamp': '2024-01-01T00:00:00',
            'value': 42.5,
            'cpu_percent': 150,  # Invalid percentage
            'labels': {'instance': 'server-01'}
        }
        
        result = validation_service.validate_mock_data(
            mock_data, sample_target_mcp, 'query_metrics', sample_scenario
        )
        
        assert result['valid'] is False
        assert any('range' in issue.lower() for issue in result['issues'])


class TestCausalityValidation:
    """Test causality relation validation"""
    
    def test_validate_causality_valid(self, validation_service, db):
        """Test validation of valid causality relation"""
        # Add actors to database
        actor1 = Actor(
            actor_type='server',
            actor_id='server-01',
            description='Test server 1'
        )
        actor2 = Actor(
            actor_type='server',
            actor_id='server-02',
            description='Test server 2'
        )
        db.create_actor(actor1)
        db.create_actor(actor2)
        
        relation = CausalityRelation(
            cause_actor='server-01',
            cause_event='high_error_rate',
            effect_actor='server-02',
            effect_event='memory_leak',
            time_delay=300,
            strength=0.8
        )
        
        actors_map = {
            'server-01': actor1,
            'server-02': actor2
        }
        
        result = validation_service.validate_causality_relation(relation, actors_map)
        
        assert result['valid'] is True
        assert len(result['issues']) == 0
    
    def test_validate_causality_missing_actor(self, validation_service):
        """Test validation with missing actor"""
        relation = CausalityRelation(
            cause_actor='server-01',
            cause_event='high_error_rate',
            effect_actor='server-02',
            effect_event='memory_leak',
            time_delay=300,
            strength=0.8
        )
        
        actors_map = {}  # No actors
        
        result = validation_service.validate_causality_relation(relation, actors_map)
        
        assert result['valid'] is False
        assert len(result['issues']) == 2  # Both actors missing
        assert any('server-01' in issue for issue in result['issues'])
        assert any('server-02' in issue for issue in result['issues'])
    
    def test_validate_causality_negative_delay(self, validation_service):
        """Test validation with negative time delay"""
        relation = CausalityRelation(
            cause_actor='server-01',
            cause_event='high_error_rate',
            effect_actor='server-02',
            effect_event='memory_leak',
            time_delay=-100,  # Invalid
            strength=0.8
        )
        
        actors_map = {
            'server-01': Actor('server', 'server-01', 'Test'),
            'server-02': Actor('server', 'server-02', 'Test')
        }
        
        result = validation_service.validate_causality_relation(relation, actors_map)
        
        assert result['valid'] is False
        assert any('negative' in issue.lower() for issue in result['issues'])
    
    def test_validate_causality_invalid_strength(self, validation_service):
        """Test validation with invalid strength"""
        relation = CausalityRelation(
            cause_actor='server-01',
            cause_event='high_error_rate',
            effect_actor='server-02',
            effect_event='memory_leak',
            time_delay=300,
            strength=1.5  # Invalid (> 1.0)
        )
        
        actors_map = {
            'server-01': Actor('server', 'server-01', 'Test'),
            'server-02': Actor('server', 'server-02', 'Test')
        }
        
        result = validation_service.validate_causality_relation(relation, actors_map)
        
        assert result['valid'] is False
        assert any('strength' in issue.lower() for issue in result['issues'])
    
    def test_validate_causality_self_reference(self, validation_service):
        """Test validation with circular self-reference"""
        relation = CausalityRelation(
            cause_actor='server-01',
            cause_event='memory_leak',
            effect_actor='server-01',
            effect_event='memory_leak',  # Same event
            time_delay=300,
            strength=0.8
        )
        
        actors_map = {
            'server-01': Actor('server', 'server-01', 'Test')
        }
        
        result = validation_service.validate_causality_relation(relation, actors_map)
        
        assert result['valid'] is False
        assert any('self-reference' in issue.lower() for issue in result['issues'])


class TestPlotConsistency:
    """Test plot graph consistency validation"""
    
    def test_validate_plot_empty_graph(self, validation_service):
        """Test validation of empty plot graph"""
        plot_graph = PlotGraph()
        
        result = validation_service.validate_plot_consistency(plot_graph)
        
        # Empty graph should have warnings but be consistent
        assert 'consistent' in result
        assert 'issues' in result
    
    def test_validate_plot_with_plot_manager(
        self, validation_service, plot_manager, db
    ):
        """Test validation using plot manager"""
        # Add actors
        actor1 = Actor('server', 'server-01', 'Test server 1')
        actor2 = Actor('server', 'server-02', 'Test server 2')
        db.create_actor(actor1)
        db.create_actor(actor2)
        
        # Add causality relation
        relation = CausalityRelation(
            cause_actor='server-01',
            cause_event='error',
            effect_actor='server-02',
            effect_event='memory_leak',
            time_delay=300,
            strength=0.8
        )
        plot_manager.add_causality_relation(relation)
        
        # Validate
        result = validation_service.validate_plot_consistency()
        
        assert 'consistent' in result
        assert 'issues' in result
        assert 'suggestions' in result


class TestDataConsistency:
    """Test data consistency checking"""
    
    def test_check_data_consistency_valid(
        self, validation_service, sample_scenario
    ):
        """Test consistency check with valid data"""
        base_time = datetime.now()
        
        data_set = [
            {
                'actor_id': 'server-01',
                'event': 'error',
                'timestamp': base_time.isoformat(),
                'value': 5.0
            },
            {
                'actor_id': 'server-02',
                'event': 'memory_leak',
                'timestamp': (base_time + timedelta(seconds=300)).isoformat(),
                'value': 8.0
            }
        ]
        
        causality_relations = [
            CausalityRelation(
                cause_actor='server-01',
                cause_event='error',
                effect_actor='server-02',
                effect_event='memory_leak',
                time_delay=300,
                strength=0.8
            )
        ]
        
        result = validation_service.check_data_consistency(
            data_set, sample_scenario, causality_relations
        )
        
        assert result['consistent'] is True
        assert len(result['issues']) == 0
    
    def test_check_data_consistency_time_violation(
        self, validation_service, sample_scenario
    ):
        """Test consistency check with time violation"""
        base_time = datetime.now()
        
        data_set = [
            {
                'actor_id': 'server-01',
                'event': 'error',
                'timestamp': base_time.isoformat(),
                'value': 5.0
            },
            {
                'actor_id': 'server-02',
                'event': 'memory_leak',
                'timestamp': (base_time - timedelta(seconds=100)).isoformat(),  # Before cause!
                'value': 8.0
            }
        ]
        
        causality_relations = [
            CausalityRelation(
                cause_actor='server-01',
                cause_event='error',
                effect_actor='server-02',
                effect_event='memory_leak',
                time_delay=300,
                strength=0.8
            )
        ]
        
        result = validation_service.check_data_consistency(
            data_set, sample_scenario, causality_relations
        )
        
        assert result['consistent'] is False
        assert len(result['issues']) > 0
        assert any('before' in issue.lower() for issue in result['issues'])
    
    def test_check_data_consistency_missing_data(
        self, validation_service, sample_scenario
    ):
        """Test consistency check with missing data"""
        data_set = [
            {
                'actor_id': 'server-01',
                'event': 'error',
                'timestamp': datetime.now().isoformat(),
                'value': 5.0
            }
            # Missing server-02 data
        ]
        
        causality_relations = [
            CausalityRelation(
                cause_actor='server-01',
                cause_event='error',
                effect_actor='server-02',
                effect_event='memory_leak',
                time_delay=300,
                strength=0.8
            )
        ]
        
        result = validation_service.check_data_consistency(
            data_set, sample_scenario, causality_relations
        )
        
        assert result['consistent'] is False
        assert any('no data found' in issue.lower() for issue in result['issues'])


class TestCorrectionSuggestions:
    """Test correction suggestion generation"""
    
    def test_generate_suggestions_from_validation_result(self, validation_service):
        """Test generating suggestions from validation result"""
        validation_result = {
            'valid': False,
            'issues': [
                'Schema validation error',
                'Invalid timestamp format'
            ],
            'suggestions': [
                'Review the schema',
                'Use ISO 8601 format'
            ]
        }
        
        suggestions = validation_service.generate_correction_suggestions(
            validation_result
        )
        
        assert len(suggestions) > 0
        assert any('schema' in s.lower() for s in suggestions)
    
    def test_generate_suggestions_circular_dependency(self, validation_service):
        """Test generating suggestions for circular dependency"""
        validation_result = {
            'consistent': False,
            'issues': [
                {
                    'type': 'circular_dependency',
                    'description': 'Circular dependency detected',
                    'affectedNodes': ['server-01', 'server-02']
                }
            ],
            'suggestions': []
        }
        
        suggestions = validation_service.generate_correction_suggestions(
            validation_result
        )
        
        assert len(suggestions) > 0
        assert any('cycle' in s.lower() or 'circular' in s.lower() for s in suggestions)
    
    def test_generate_suggestions_deduplication(self, validation_service):
        """Test that suggestions are deduplicated"""
        validation_result = {
            'valid': False,
            'issues': ['Schema error', 'Schema error'],
            'suggestions': ['Review schema', 'Review schema']
        }
        
        suggestions = validation_service.generate_correction_suggestions(
            validation_result
        )
        
        # Should deduplicate
        assert len(suggestions) == len(set(suggestions))


class TestHelperMethods:
    """Test helper methods"""
    
    def test_extract_timestamp_from_dict(self, validation_service):
        """Test extracting timestamp from dictionary"""
        data = {
            'timestamp': '2024-01-01T00:00:00',
            'value': 42
        }
        
        ts = validation_service._extract_timestamp(data)
        
        assert ts is not None
        assert isinstance(ts, datetime)
    
    def test_extract_timestamp_datetime_object(self, validation_service):
        """Test extracting datetime object"""
        now = datetime.now()
        data = {
            'timestamp': now,
            'value': 42
        }
        
        ts = validation_service._extract_timestamp(data)
        
        assert ts == now
    
    def test_extract_timestamp_not_found(self, validation_service):
        """Test extracting timestamp when not present"""
        data = {
            'value': 42
        }
        
        ts = validation_service._extract_timestamp(data)
        
        assert ts is None
    
    def test_extract_keywords(self, validation_service):
        """Test keyword extraction"""
        text = "Memory leak scenario with server errors"
        
        keywords = validation_service._extract_keywords(text)
        
        assert 'memory' in keywords
        assert 'leak' in keywords
        assert 'scenario' in keywords
        assert 'server' in keywords
        assert 'errors' in keywords
