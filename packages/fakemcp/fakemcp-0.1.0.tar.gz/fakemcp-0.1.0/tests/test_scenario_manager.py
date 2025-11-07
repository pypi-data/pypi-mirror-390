"""
Tests for Scenario Manager
"""

import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from fakemcp.database import Database
from fakemcp.models import Actor, CausalityRelation, TargetMCP
from fakemcp.scenario_manager import ScenarioManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = Database(db_path)
    yield db
    
    db.close()
    os.unlink(db_path)


@pytest.fixture
def scenario_manager(temp_db):
    """Create a scenario manager with temporary database"""
    return ScenarioManager(temp_db)


def test_create_scenario(scenario_manager):
    """Test creating a new scenario"""
    description = "模拟内存泄露场景，server-01 内存从 2GB 增长到 8GB"
    target_mcps = ["prometheus", "cloudmonitoring"]
    
    scenario = scenario_manager.create_scenario(description, target_mcps)
    
    assert scenario.id.startswith("scenario_")
    assert scenario.description == description
    assert scenario.target_mcps == target_mcps
    assert isinstance(scenario.created_at, datetime)
    assert isinstance(scenario.updated_at, datetime)
    assert 'keywords' in scenario.metadata
    assert len(scenario.metadata['keywords']) > 0


def test_get_scenario(scenario_manager):
    """Test retrieving a scenario"""
    scenario = scenario_manager.create_scenario("Test scenario")
    
    retrieved = scenario_manager.get_scenario(scenario.id)
    
    assert retrieved is not None
    assert retrieved.id == scenario.id
    assert retrieved.description == scenario.description


def test_get_nonexistent_scenario(scenario_manager):
    """Test retrieving a non-existent scenario"""
    result = scenario_manager.get_scenario("nonexistent_id")
    assert result is None


def test_update_scenario(scenario_manager):
    """Test updating a scenario"""
    scenario = scenario_manager.create_scenario("Original description")
    original_updated_at = scenario.updated_at
    
    # Update description
    updated = scenario_manager.update_scenario(
        scenario.id,
        description="Updated description"
    )
    
    assert updated is not None
    assert updated.description == "Updated description"
    assert updated.updated_at > original_updated_at


def test_update_scenario_target_mcps(scenario_manager):
    """Test updating scenario target MCPs"""
    scenario = scenario_manager.create_scenario("Test", ["mcp1"])
    
    updated = scenario_manager.update_scenario(
        scenario.id,
        target_mcps=["mcp1", "mcp2", "mcp3"]
    )
    
    assert updated is not None
    assert len(updated.target_mcps) == 3
    assert "mcp2" in updated.target_mcps


def test_update_scenario_metadata(scenario_manager):
    """Test updating scenario metadata"""
    scenario = scenario_manager.create_scenario("Test")
    
    updated = scenario_manager.update_scenario(
        scenario.id,
        metadata_updates={'custom_field': 'custom_value'}
    )
    
    assert updated is not None
    assert updated.metadata['custom_field'] == 'custom_value'


def test_delete_scenario(scenario_manager):
    """Test deleting a scenario"""
    scenario = scenario_manager.create_scenario("Test scenario")
    
    result = scenario_manager.delete_scenario(scenario.id)
    assert result is True
    
    # Verify it's deleted
    retrieved = scenario_manager.get_scenario(scenario.id)
    assert retrieved is None


def test_delete_nonexistent_scenario(scenario_manager):
    """Test deleting a non-existent scenario"""
    result = scenario_manager.delete_scenario("nonexistent_id")
    assert result is False


def test_list_scenarios(scenario_manager):
    """Test listing all scenarios"""
    scenario_manager.create_scenario("Scenario 1")
    scenario_manager.create_scenario("Scenario 2")
    scenario_manager.create_scenario("Scenario 3")
    
    scenarios = scenario_manager.list_scenarios()
    
    assert len(scenarios) == 3
    descriptions = [s.description for s in scenarios]
    assert "Scenario 1" in descriptions
    assert "Scenario 2" in descriptions
    assert "Scenario 3" in descriptions


def test_extract_keywords_chinese(scenario_manager):
    """Test keyword extraction from Chinese text"""
    description = "模拟内存泄露场景，server-01 的内存从 2GB 增长到 8GB"
    keywords = scenario_manager._extract_keywords(description)
    
    assert "server-01" in keywords
    assert "2GB" in keywords or "8GB" in keywords
    # Check that Chinese phrases are extracted (may be longer phrases)
    assert any("内存" in kw for kw in keywords)
    assert any("模拟" in kw for kw in keywords)


def test_extract_keywords_english(scenario_manager):
    """Test keyword extraction from English text"""
    description = "Simulate memory leak scenario where server-01 memory grows from 2GB to 8GB"
    keywords = scenario_manager._extract_keywords(description)
    
    assert "server-01" in keywords
    assert "memory" in keywords
    assert "leak" in keywords


def test_extract_keywords_mixed(scenario_manager):
    """Test keyword extraction from mixed Chinese-English text"""
    description = "测试 Prometheus 监控 server-01 的 CPU 使用率"
    keywords = scenario_manager._extract_keywords(description)
    
    assert "Prometheus" in keywords
    assert "server-01" in keywords
    assert "CPU" in keywords


def test_save_to_file(scenario_manager, temp_db):
    """Test saving scenario to YAML file"""
    # Create scenario with related data
    scenario = scenario_manager.create_scenario(
        "Memory leak scenario",
        ["prometheus"]
    )
    
    # Add target MCP
    target_mcp = TargetMCP(
        id="prometheus",
        name="Prometheus",
        url="http://localhost:9090",
        config={},
        schema={},
        actor_fields=["instance"]
    )
    temp_db.create_target_mcp(target_mcp)
    
    # Add actor
    actor = Actor(
        actor_type="server",
        actor_id="server-01",
        description="Memory leak server"
    )
    temp_db.create_actor(actor)
    
    # Add causality relation
    relation = CausalityRelation(
        cause_actor="server-02",
        cause_event="error_rate_high",
        effect_actor="server-01",
        effect_event="memory_leak",
        time_delay=300
    )
    temp_db.create_causality_relation(relation)
    
    # Save to file
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        filepath = f.name
    
    try:
        result = scenario_manager.save_to_file(scenario.id, filepath)
        assert result is True
        assert Path(filepath).exists()
        
        # Verify file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "Memory leak scenario" in content
            assert "prometheus" in content
            assert "server-01" in content
    finally:
        if Path(filepath).exists():
            os.unlink(filepath)


def test_load_from_file(scenario_manager, temp_db):
    """Test loading scenario from YAML file"""
    # Create and save a scenario
    original_scenario = scenario_manager.create_scenario(
        "Test scenario for loading",
        ["test_mcp"]
    )
    
    target_mcp = TargetMCP(
        id="test_mcp",
        name="Test MCP",
        url="http://test.com",
        config={},
        schema={},
        actor_fields=["test_field"]
    )
    temp_db.create_target_mcp(target_mcp)
    
    actor = Actor(
        actor_type="test_type",
        actor_id="test_id",
        description="Test actor"
    )
    temp_db.create_actor(actor)
    
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        filepath = f.name
    
    try:
        scenario_manager.save_to_file(original_scenario.id, filepath)
        
        # Clear database
        temp_db.clear_all_data()
        
        # Load from file
        loaded_scenario = scenario_manager.load_from_file(filepath)
        
        assert loaded_scenario is not None
        assert loaded_scenario.id == original_scenario.id
        assert loaded_scenario.description == original_scenario.description
        
        # Verify related data was loaded
        loaded_mcp = temp_db.get_target_mcp("test_mcp")
        assert loaded_mcp is not None
        assert loaded_mcp.name == "Test MCP"
        
        loaded_actor = temp_db.get_actor("test_type", "test_id")
        assert loaded_actor is not None
        assert loaded_actor.description == "Test actor"
    finally:
        if Path(filepath).exists():
            os.unlink(filepath)


def test_load_from_nonexistent_file(scenario_manager):
    """Test loading from non-existent file"""
    result = scenario_manager.load_from_file("/nonexistent/path/file.yaml")
    assert result is None
