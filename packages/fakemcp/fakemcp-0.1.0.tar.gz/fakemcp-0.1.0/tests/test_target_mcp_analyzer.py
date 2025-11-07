"""
Tests for Target MCP Analyzer
"""

import json
import os
import tempfile
from pathlib import Path

import httpx
import pytest

from fakemcp.config import Config
from fakemcp.database import Database
from fakemcp.target_mcp_analyzer import TargetMCPAnalyzer


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    db = Database(db_path)
    yield db
    
    db.close()
    os.unlink(db_path)


@pytest.fixture
def temp_cache_dir():
    """Create a temporary cache directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Temporarily override the cache directory
        original_cache_dir = Config.CACHE_DIR
        Config.CACHE_DIR = tmpdir
        yield tmpdir
        Config.CACHE_DIR = original_cache_dir


@pytest.fixture
async def analyzer(temp_db, temp_cache_dir):
    """Create a TargetMCPAnalyzer instance"""
    analyzer = TargetMCPAnalyzer(temp_db)
    yield analyzer
    await analyzer.close()


def test_identify_actor_fields_basic():
    """Test basic actor field identification"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        analyzer = TargetMCPAnalyzer(db)
        
        schema = {
            "tools": [
                {
                    "name": "query_metrics",
                    "inputSchema": {
                        "properties": {
                            "server_id": {"type": "string"},
                            "metric_name": {"type": "string"},
                            "instance": {"type": "string"},
                            "job": {"type": "string"}
                        }
                    }
                }
            ]
        }
        
        actor_fields = analyzer.identify_actor_fields(schema)
        
        assert "server_id" in actor_fields
        assert "instance" in actor_fields
        assert "job" in actor_fields
        assert "metric_name" not in actor_fields
        
        db.close()
    finally:
        os.unlink(db_path)


def test_identify_actor_fields_with_descriptions():
    """Test actor field identification using descriptions"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        analyzer = TargetMCPAnalyzer(db)
        
        schema = {
            "tools": [
                {
                    "name": "get_weather",
                    "inputSchema": {
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City identifier for weather query"
                            },
                            "temperature_unit": {
                                "type": "string",
                                "description": "Unit for temperature"
                            }
                        }
                    }
                }
            ]
        }
        
        actor_fields = analyzer.identify_actor_fields(schema)
        
        assert "location" in actor_fields
        assert "temperature_unit" not in actor_fields
        
        db.close()
    finally:
        os.unlink(db_path)


def test_identify_actor_fields_multiple_tools():
    """Test actor field identification across multiple tools"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        analyzer = TargetMCPAnalyzer(db)
        
        schema = {
            "tools": [
                {
                    "name": "tool1",
                    "inputSchema": {
                        "properties": {
                            "user_id": {"type": "string"},
                            "data": {"type": "string"}
                        }
                    }
                },
                {
                    "name": "tool2",
                    "inputSchema": {
                        "properties": {
                            "resource_id": {"type": "string"},
                            "hostname": {"type": "string"}
                        }
                    }
                }
            ]
        }
        
        actor_fields = analyzer.identify_actor_fields(schema)
        
        assert "user_id" in actor_fields
        assert "resource_id" in actor_fields
        assert "hostname" in actor_fields
        assert "data" not in actor_fields
        
        db.close()
    finally:
        os.unlink(db_path)


def test_cache_schema(temp_db, temp_cache_dir):
    """Test schema caching"""
    analyzer = TargetMCPAnalyzer(temp_db)
    
    schema = {
        "tools": [
            {"name": "test_tool", "inputSchema": {"properties": {}}}
        ]
    }
    
    analyzer._cache_schema("test-target", schema)
    
    # Check cache file exists
    cache_file = Path(temp_cache_dir) / "test-target_schema.json"
    assert cache_file.exists()
    
    # Verify cached content
    cached = analyzer._get_cached_schema("test-target")
    assert cached == schema


def test_cache_data(temp_db, temp_cache_dir):
    """Test data caching"""
    analyzer = TargetMCPAnalyzer(temp_db)
    
    parameters = {"server_id": "server-01", "metric": "memory"}
    data = {"value": 8192, "unit": "MB"}
    
    analyzer._cache_data("test-target", "query_metrics", parameters, data)
    
    # Retrieve from cache
    cached = analyzer._get_cached_data("test-target", "query_metrics", parameters)
    assert cached == data


def test_cache_data_different_parameters(temp_db, temp_cache_dir):
    """Test that different parameters create different cache entries"""
    analyzer = TargetMCPAnalyzer(temp_db)
    
    params1 = {"server_id": "server-01"}
    params2 = {"server_id": "server-02"}
    data1 = {"value": 100}
    data2 = {"value": 200}
    
    analyzer._cache_data("test-target", "tool", params1, data1)
    analyzer._cache_data("test-target", "tool", params2, data2)
    
    cached1 = analyzer._get_cached_data("test-target", "tool", params1)
    cached2 = analyzer._get_cached_data("test-target", "tool", params2)
    
    assert cached1 == data1
    assert cached2 == data2


def test_clear_cache_specific_target(temp_db, temp_cache_dir):
    """Test clearing cache for a specific target"""
    analyzer = TargetMCPAnalyzer(temp_db)
    
    # Cache data for two targets
    analyzer._cache_schema("target1", {"tools": []})
    analyzer._cache_schema("target2", {"tools": []})
    
    # Clear only target1
    analyzer.clear_cache("target1")
    
    # target1 should be cleared, target2 should remain
    assert analyzer._get_cached_schema("target1") is None
    assert analyzer._get_cached_schema("target2") is not None


def test_clear_cache_all(temp_db, temp_cache_dir):
    """Test clearing all cache"""
    analyzer = TargetMCPAnalyzer(temp_db)
    
    # Cache data for multiple targets
    analyzer._cache_schema("target1", {"tools": []})
    analyzer._cache_schema("target2", {"tools": []})
    analyzer._cache_data("target1", "tool", {}, {"data": "test"})
    
    # Clear all cache
    analyzer.clear_cache()
    
    # All should be cleared
    assert analyzer._get_cached_schema("target1") is None
    assert analyzer._get_cached_schema("target2") is None
    assert len(list(Path(temp_cache_dir).glob("*.json"))) == 0


def test_is_actor_field_patterns():
    """Test _is_actor_field method with various patterns"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        db_path = f.name
    
    try:
        db = Database(db_path)
        analyzer = TargetMCPAnalyzer(db)
        
        # Should match
        assert analyzer._is_actor_field("server_id")
        assert analyzer._is_actor_field("user_id")
        assert analyzer._is_actor_field("resource_id")
        assert analyzer._is_actor_field("server_name")
        assert analyzer._is_actor_field("hostname")
        assert analyzer._is_actor_field("instance")
        assert analyzer._is_actor_field("instance_id")
        assert analyzer._is_actor_field("job")
        assert analyzer._is_actor_field("application")
        assert analyzer._is_actor_field("service")
        assert analyzer._is_actor_field("city_name")
        assert analyzer._is_actor_field("location_id")
        
        # Should not match
        assert not analyzer._is_actor_field("metric_name")
        assert not analyzer._is_actor_field("value")
        assert not analyzer._is_actor_field("timestamp")
        assert not analyzer._is_actor_field("data")
        assert not analyzer._is_actor_field("config")
        
        db.close()
    finally:
        os.unlink(db_path)
