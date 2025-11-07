"""
FakeMCP - A MCP server simulator for testing AI Agents

FakeMCP is a special MCP (Model Context Protocol) server that simulates
other MCP servers' behavior based on scenario descriptions and real MCP
server configurations.
"""

__version__ = "0.1.0"
__author__ = "FakeMCP Team"

from fakemcp.models import (
    Scenario,
    Actor,
    TargetMCP,
    CausalityRelation,
    PlotNode,
    WorkflowState,
)
from fakemcp.database import Database

__all__ = [
    "Scenario",
    "Actor",
    "TargetMCP",
    "CausalityRelation",
    "PlotNode",
    "WorkflowState",
    "Database",
]
