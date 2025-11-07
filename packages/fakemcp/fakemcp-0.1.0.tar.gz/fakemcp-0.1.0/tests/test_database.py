"""
Tests for database layer
"""

import os
import tempfile
from datetime import datetime

from fakemcp.database import Database
from fakemcp.models import (
    Actor,
    CausalityRelation,
    PlotNode,
    Scenario,
    TargetMCP,
    WorkflowState,
)


def test_scenario_crud():
    """Test Scenario CRUD operations"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        # Create
        scenario = Scenario(
            id="test-scenario-1",
            description="Test memory leak scenario",
            target_mcps=["prometheus", "cloudmonitoring"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"key": "value"}
        )
        db.create_scenario(scenario)
        
        # Read
        retrieved = db.get_scenario("test-scenario-1")
        assert retrieved is not None
        assert retrieved.id == "test-scenario-1"
        assert retrieved.description == "Test memory leak scenario"
        assert len(retrieved.target_mcps) == 2
        
        # Update
        scenario.description = "Updated description"
        scenario.updated_at = datetime.now()
        db.update_scenario(scenario)
        
        updated = db.get_scenario("test-scenario-1")
        assert updated.description == "Updated description"
        
        # List
        scenarios = db.list_scenarios()
        assert len(scenarios) == 1
        
        # Delete
        db.delete_scenario("test-scenario-1")
        deleted = db.get_scenario("test-scenario-1")
        assert deleted is None
        
        db.close()
    finally:
        os.unlink(db_path)


def test_actor_crud():
    """Test Actor CRUD operations"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        # Create
        actor = Actor(
            actor_type="server",
            actor_id="server-01",
            description="Memory leak server",
            state={"memory": "8GB"},
            parent_actor=None,
            metadata={"region": "us-west"}
        )
        db.create_actor(actor)
        
        # Read
        retrieved = db.get_actor("server", "server-01")
        assert retrieved is not None
        assert retrieved.actor_id == "server-01"
        assert retrieved.state["memory"] == "8GB"
        
        # Update
        actor.description = "Updated server"
        db.update_actor(actor)
        
        updated = db.get_actor("server", "server-01")
        assert updated.description == "Updated server"
        
        # List
        actors = db.list_actors()
        assert len(actors) == 1
        
        # Delete
        db.delete_actor("server", "server-01")
        deleted = db.get_actor("server", "server-01")
        assert deleted is None
        
        db.close()
    finally:
        os.unlink(db_path)


def test_target_mcp_crud():
    """Test TargetMCP CRUD operations"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        # Create
        target = TargetMCP(
            id="prometheus-1",
            name="Prometheus",
            url="http://localhost:9090",
            config={"timeout": 30},
            schema={"tools": []},
            actor_fields=["instance", "job"],
            example_data={"query": "result"},
            connected=True
        )
        db.create_target_mcp(target)
        
        # Read
        retrieved = db.get_target_mcp("prometheus-1")
        assert retrieved is not None
        assert retrieved.name == "Prometheus"
        assert retrieved.connected is True
        
        # Update
        target.connected = False
        db.update_target_mcp(target)
        
        updated = db.get_target_mcp("prometheus-1")
        assert updated.connected is False
        
        # List
        targets = db.list_target_mcps()
        assert len(targets) == 1
        
        # Delete
        db.delete_target_mcp("prometheus-1")
        deleted = db.get_target_mcp("prometheus-1")
        assert deleted is None
        
        db.close()
    finally:
        os.unlink(db_path)


def test_causality_relation_crud():
    """Test CausalityRelation CRUD operations"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        # Create
        relation = CausalityRelation(
            cause_actor="server-02",
            cause_event="error_rate_high",
            effect_actor="server-01",
            effect_event="memory_leak",
            time_delay=300,
            strength=0.8
        )
        relation_id = db.create_causality_relation(relation)
        assert relation_id > 0
        
        # Read
        retrieved = db.get_causality_relation(relation_id)
        assert retrieved is not None
        assert retrieved.cause_actor == "server-02"
        assert retrieved.time_delay == 300
        
        # List
        relations = db.list_causality_relations()
        assert len(relations) == 1
        
        # Delete
        db.delete_causality_relation(relation_id)
        deleted = db.get_causality_relation(relation_id)
        assert deleted is None
        
        db.close()
    finally:
        os.unlink(db_path)


def test_plot_node_crud():
    """Test PlotNode CRUD operations"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        # Create
        node = PlotNode(
            id="node-1",
            actor="server-01",
            event="memory_leak",
            timestamp_offset=300,
            data_pattern={"trend": "increasing"},
            children=["node-2", "node-3"]
        )
        db.create_plot_node(node)
        
        # Read
        retrieved = db.get_plot_node("node-1")
        assert retrieved is not None
        assert retrieved.actor == "server-01"
        assert len(retrieved.children) == 2
        
        # Update
        node.event = "memory_critical"
        db.update_plot_node(node)
        
        updated = db.get_plot_node("node-1")
        assert updated.event == "memory_critical"
        
        # List
        nodes = db.list_plot_nodes()
        assert len(nodes) == 1
        
        # Delete
        db.delete_plot_node("node-1")
        deleted = db.get_plot_node("node-1")
        assert deleted is None
        
        db.close()
    finally:
        os.unlink(db_path)


def test_workflow_state():
    """Test WorkflowState operations"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        
        # Save
        state = WorkflowState(
            stage="actor_analysis",
            data={"actors": ["server-01"]},
            history=[{"stage": "init", "timestamp": "2024-01-01"}],
            plot_suggestions=[{"type": "root_cause", "description": "test"}]
        )
        db.save_workflow_state(state)
        
        # Read
        retrieved = db.get_workflow_state()
        assert retrieved is not None
        assert retrieved.stage == "actor_analysis"
        assert len(retrieved.history) == 1
        
        # Update (replace)
        state.stage = "data_generation"
        db.save_workflow_state(state)
        
        updated = db.get_workflow_state()
        assert updated.stage == "data_generation"
        
        # Clear
        db.clear_workflow_state()
        cleared = db.get_workflow_state()
        assert cleared is None
        
        db.close()
    finally:
        os.unlink(db_path)
