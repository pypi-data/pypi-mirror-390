"""
Data models for FakeMCP
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Scenario:
    """场景配置"""
    id: str
    description: str
    target_mcps: List[str]
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalityRelation:
    """因果关系"""
    cause_actor: str
    cause_event: str
    effect_actor: str
    effect_event: str
    time_delay: int = 0
    strength: float = 1.0


@dataclass
class PlotNode:
    """剧情节点"""
    id: str
    actor: str
    event: str
    timestamp_offset: int
    data_pattern: Dict[str, Any]
    children: List[str] = field(default_factory=list)


@dataclass
class Actor:
    """角色实体"""
    actor_type: str
    actor_id: str
    description: str
    state: Dict[str, Any] = field(default_factory=dict)
    parent_actor: Optional[Dict[str, str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TargetMCP:
    """目标 MCP 服务器"""
    id: str
    name: str
    url: str
    config: Dict[str, Any]
    schema: Dict[str, Any]
    actor_fields: List[str] = field(default_factory=list)
    example_data: Dict[str, Any] = field(default_factory=dict)
    connected: bool = False


@dataclass
class WorkflowState:
    """工作流状态"""
    stage: str
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    plot_suggestions: List[Dict[str, Any]] = field(default_factory=list)
