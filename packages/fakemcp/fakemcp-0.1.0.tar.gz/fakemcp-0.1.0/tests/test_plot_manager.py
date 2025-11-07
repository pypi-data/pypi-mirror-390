"""
Tests for PlotManager
"""

import pytest
from datetime import datetime

from fakemcp.database import Database
from fakemcp.plot_manager import PlotManager, PlotGraph
from fakemcp.models import CausalityRelation, Scenario, Actor


@pytest.fixture
def db():
    """Create a test database"""
    database = Database(":memory:")
    yield database
    database.close()


@pytest.fixture
def plot_manager(db):
    """Create a PlotManager instance"""
    return PlotManager(db)


@pytest.fixture
def sample_scenario(db):
    """Create a sample scenario"""
    scenario = Scenario(
        id="test-scenario",
        description="Memory leak scenario",
        target_mcps=["prometheus", "cloudmonitoring", "logging"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={}
    )
    db.create_scenario(scenario)
    return scenario


@pytest.fixture
def sample_actors(db):
    """Create sample actors"""
    actors = [
        Actor(
            actor_type="server",
            actor_id="server-01",
            description="Server with memory leak",
            state={},
            metadata={}
        ),
        Actor(
            actor_type="server",
            actor_id="server-02",
            description="Server causing errors",
            state={},
            metadata={}
        )
    ]
    for actor in actors:
        db.create_actor(actor)
    return actors


def test_add_causality_relation(plot_manager):
    """Test adding a causality relation"""
    relation = CausalityRelation(
        cause_actor="server-02",
        cause_event="error_rate_high",
        effect_actor="server-01",
        effect_event="memory_leak",
        time_delay=300,
        strength=0.8
    )
    
    relation_id = plot_manager.add_causality_relation(relation)
    
    assert relation_id is not None
    assert isinstance(relation_id, str)
    
    # Verify it was stored
    relations = plot_manager.db.list_causality_relations()
    assert len(relations) == 1
    assert relations[0].cause_actor == "server-02"
    assert relations[0].effect_actor == "server-01"


def test_build_plot_graph_empty(plot_manager):
    """Test building an empty plot graph"""
    plot_graph = plot_manager.build_plot_graph()
    
    assert isinstance(plot_graph, PlotGraph)
    assert len(plot_graph.nodes) == 0
    assert len(plot_graph.edges) == 0


def test_build_plot_graph_single_relation(plot_manager):
    """Test building a plot graph with a single relation"""
    relation = CausalityRelation(
        cause_actor="server-02",
        cause_event="error_rate_high",
        effect_actor="server-01",
        effect_event="memory_leak",
        time_delay=300,
        strength=1.0
    )
    plot_manager.add_causality_relation(relation)
    
    plot_graph = plot_manager.build_plot_graph()
    
    assert len(plot_graph.nodes) == 2
    assert len(plot_graph.edges) == 1
    
    # Check nodes
    cause_node = None
    effect_node = None
    for node in plot_graph.nodes.values():
        if node.actor == "server-02":
            cause_node = node
        elif node.actor == "server-01":
            effect_node = node
    
    assert cause_node is not None
    assert effect_node is not None
    assert cause_node.timestamp_offset == 0
    assert effect_node.timestamp_offset == 300


def test_build_plot_graph_chain(plot_manager):
    """Test building a plot graph with a chain of relations"""
    relations = [
        CausalityRelation(
            cause_actor="server-02",
            cause_event="error_rate_high",
            effect_actor="server-01",
            effect_event="memory_leak",
            time_delay=300,
            strength=1.0
        ),
        CausalityRelation(
            cause_actor="server-01",
            cause_event="memory_leak",
            effect_actor="server-01",
            effect_event="response_slow",
            time_delay=600,
            strength=1.0
        )
    ]
    
    for relation in relations:
        plot_manager.add_causality_relation(relation)
    
    plot_graph = plot_manager.build_plot_graph()
    
    assert len(plot_graph.nodes) == 3
    assert len(plot_graph.edges) == 2
    
    # Check timestamp offsets
    for node in plot_graph.nodes.values():
        if node.actor == "server-02" and node.event == "error_rate_high":
            assert node.timestamp_offset == 0
        elif node.actor == "server-01" and node.event == "memory_leak":
            assert node.timestamp_offset == 300
        elif node.actor == "server-01" and node.event == "response_slow":
            assert node.timestamp_offset == 900


def test_validate_plot_consistency_valid(plot_manager, sample_actors):
    """Test validating a consistent plot"""
    relation = CausalityRelation(
        cause_actor="server-02",
        cause_event="error_rate_high",
        effect_actor="server-01",
        effect_event="memory_leak",
        time_delay=300,
        strength=1.0
    )
    plot_manager.add_causality_relation(relation)
    
    result = plot_manager.validate_plot_consistency()
    
    assert result['consistent'] is True
    assert len(result['issues']) == 0
    assert len(result['suggestions']) == 0


def test_validate_plot_consistency_circular_dependency(plot_manager, sample_actors):
    """Test detecting circular dependencies"""
    relations = [
        CausalityRelation(
            cause_actor="server-01",
            cause_event="event_a",
            effect_actor="server-02",
            effect_event="event_b",
            time_delay=100,
            strength=1.0
        ),
        CausalityRelation(
            cause_actor="server-02",
            cause_event="event_b",
            effect_actor="server-01",
            effect_event="event_a",
            time_delay=100,
            strength=1.0
        )
    ]
    
    for relation in relations:
        plot_manager.add_causality_relation(relation)
    
    result = plot_manager.validate_plot_consistency()
    
    assert result['consistent'] is False
    assert len(result['issues']) > 0
    assert any(issue['type'] == 'circular_dependency' for issue in result['issues'])


def test_validate_plot_consistency_missing_actor(plot_manager):
    """Test detecting missing actors"""
    relation = CausalityRelation(
        cause_actor="missing-server",
        cause_event="error",
        effect_actor="server-01",
        effect_event="memory_leak",
        time_delay=300,
        strength=1.0
    )
    plot_manager.add_causality_relation(relation)
    
    result = plot_manager.validate_plot_consistency()
    
    assert result['consistent'] is False
    assert len(result['issues']) > 0
    assert any(issue['type'] == 'missing_actor' for issue in result['issues'])


def test_get_timeline_empty(plot_manager):
    """Test getting timeline from empty plot"""
    timeline = plot_manager.get_timeline()
    
    assert isinstance(timeline, list)
    assert len(timeline) == 0


def test_get_timeline_single_relation(plot_manager):
    """Test getting timeline with a single relation"""
    relation = CausalityRelation(
        cause_actor="server-02",
        cause_event="error_rate_high",
        effect_actor="server-01",
        effect_event="memory_leak",
        time_delay=300,
        strength=1.0
    )
    plot_manager.add_causality_relation(relation)
    
    timeline = plot_manager.get_timeline()
    
    assert len(timeline) == 2
    assert timeline[0]['timestamp'] == 0
    assert timeline[1]['timestamp'] == 300
    assert 'server-02:error_rate_high' in timeline[0]['events']
    assert 'server-01:memory_leak' in timeline[1]['events']


def test_get_timeline_chain(plot_manager):
    """Test getting timeline with a chain of relations"""
    relations = [
        CausalityRelation(
            cause_actor="server-02",
            cause_event="error_rate_high",
            effect_actor="server-01",
            effect_event="memory_leak",
            time_delay=300,
            strength=1.0
        ),
        CausalityRelation(
            cause_actor="server-01",
            cause_event="memory_leak",
            effect_actor="server-01",
            effect_event="response_slow",
            time_delay=600,
            strength=1.0
        )
    ]
    
    for relation in relations:
        plot_manager.add_causality_relation(relation)
    
    timeline = plot_manager.get_timeline()
    
    assert len(timeline) == 3
    assert timeline[0]['timestamp'] == 0
    assert timeline[1]['timestamp'] == 300
    assert timeline[2]['timestamp'] == 900


def test_generate_plot_expansion_prompt(plot_manager, sample_scenario, sample_actors):
    """Test generating plot expansion prompt"""
    result = plot_manager.generate_plot_expansion_prompt(
        actor_id="server-01",
        event="memory_leak",
        scenario=sample_scenario
    )
    
    assert 'promptForAI' in result
    assert 'currentActors' in result
    assert 'targetMcps' in result
    assert 'exampleFormat' in result
    
    assert isinstance(result['promptForAI'], str)
    assert len(result['promptForAI']) > 0
    assert 'server-01' in result['promptForAI']
    assert 'memory_leak' in result['promptForAI']
    
    assert 'server-01' in result['currentActors']
    assert 'server-02' in result['currentActors']
    
    assert 'prometheus' in result['targetMcps']


def test_plot_graph_to_dict(plot_manager):
    """Test converting plot graph to dictionary"""
    relation = CausalityRelation(
        cause_actor="server-02",
        cause_event="error_rate_high",
        effect_actor="server-01",
        effect_event="memory_leak",
        time_delay=300,
        strength=0.8
    )
    plot_manager.add_causality_relation(relation)
    
    plot_graph = plot_manager.build_plot_graph()
    result = plot_graph.to_dict()
    
    assert 'nodes' in result
    assert 'edges' in result
    assert len(result['nodes']) == 2
    assert len(result['edges']) == 1
    
    # Check edge structure
    edge = result['edges'][0]
    assert edge['cause_actor'] == 'server-02'
    assert edge['effect_actor'] == 'server-01'
    assert edge['time_delay'] == 300
    assert edge['strength'] == 0.8
