"""
Database layer for FakeMCP using SQLite
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fakemcp.models import (
    Actor,
    CausalityRelation,
    PlotNode,
    Scenario,
    TargetMCP,
    WorkflowState,
)


class Database:
    """SQLite database manager for FakeMCP"""

    def __init__(self, db_path: str = "fakemcp.db"):
        """Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._ensure_db_directory()
        self._connect()
        self._create_tables()

    def _ensure_db_directory(self):
        """Ensure database directory exists"""
        db_dir = Path(self.db_path).parent
        if db_dir != Path('.'):
            db_dir.mkdir(parents=True, exist_ok=True)

    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def _create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()

        # Scenarios table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scenarios (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL,
                target_mcps TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Actors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS actors (
                actor_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                description TEXT NOT NULL,
                state TEXT,
                parent_actor TEXT,
                metadata TEXT,
                PRIMARY KEY (actor_type, actor_id)
            )
        """)

        # Target MCPs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS target_mcps (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                url TEXT NOT NULL,
                config TEXT,
                schema TEXT,
                actor_fields TEXT,
                example_data TEXT,
                connected INTEGER DEFAULT 0
            )
        """)

        # Causality Relations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS causality_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cause_actor TEXT NOT NULL,
                cause_event TEXT NOT NULL,
                effect_actor TEXT NOT NULL,
                effect_event TEXT NOT NULL,
                time_delay INTEGER DEFAULT 0,
                strength REAL DEFAULT 1.0
            )
        """)

        # Plot Nodes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plot_nodes (
                id TEXT PRIMARY KEY,
                actor TEXT NOT NULL,
                event TEXT NOT NULL,
                timestamp_offset INTEGER NOT NULL,
                data_pattern TEXT,
                children TEXT
            )
        """)

        # Workflow State table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                stage TEXT NOT NULL,
                data TEXT,
                history TEXT,
                plot_suggestions TEXT
            )
        """)

        self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None

    # Scenario CRUD operations
    def create_scenario(self, scenario: Scenario) -> None:
        """Create a new scenario"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO scenarios (id, description, target_mcps, created_at, updated_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            scenario.id,
            scenario.description,
            json.dumps(scenario.target_mcps),
            scenario.created_at.isoformat(),
            scenario.updated_at.isoformat(),
            json.dumps(scenario.metadata)
        ))
        self.conn.commit()

    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """Get scenario by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,))
        row = cursor.fetchone()
        
        if row:
            return Scenario(
                id=row['id'],
                description=row['description'],
                target_mcps=json.loads(row['target_mcps']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
        return None

    def update_scenario(self, scenario: Scenario) -> None:
        """Update an existing scenario"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE scenarios
            SET description = ?, target_mcps = ?, updated_at = ?, metadata = ?
            WHERE id = ?
        """, (
            scenario.description,
            json.dumps(scenario.target_mcps),
            scenario.updated_at.isoformat(),
            json.dumps(scenario.metadata),
            scenario.id
        ))
        self.conn.commit()

    def delete_scenario(self, scenario_id: str) -> None:
        """Delete a scenario"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM scenarios WHERE id = ?", (scenario_id,))
        self.conn.commit()

    def list_scenarios(self) -> List[Scenario]:
        """List all scenarios"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM scenarios")
        rows = cursor.fetchall()
        
        return [
            Scenario(
                id=row['id'],
                description=row['description'],
                target_mcps=json.loads(row['target_mcps']),
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            for row in rows
        ]

    # Actor CRUD operations
    def create_actor(self, actor: Actor) -> None:
        """Create a new actor"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO actors (actor_type, actor_id, description, state, parent_actor, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            actor.actor_type,
            actor.actor_id,
            actor.description,
            json.dumps(actor.state),
            json.dumps(actor.parent_actor) if actor.parent_actor else None,
            json.dumps(actor.metadata)
        ))
        self.conn.commit()

    def get_actor(self, actor_type: str, actor_id: str) -> Optional[Actor]:
        """Get actor by type and ID"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM actors WHERE actor_type = ? AND actor_id = ?",
            (actor_type, actor_id)
        )
        row = cursor.fetchone()
        
        if row:
            return Actor(
                actor_type=row['actor_type'],
                actor_id=row['actor_id'],
                description=row['description'],
                state=json.loads(row['state']) if row['state'] else {},
                parent_actor=json.loads(row['parent_actor']) if row['parent_actor'] else None,
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
        return None

    def update_actor(self, actor: Actor) -> None:
        """Update an existing actor"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE actors
            SET description = ?, state = ?, parent_actor = ?, metadata = ?
            WHERE actor_type = ? AND actor_id = ?
        """, (
            actor.description,
            json.dumps(actor.state),
            json.dumps(actor.parent_actor) if actor.parent_actor else None,
            json.dumps(actor.metadata),
            actor.actor_type,
            actor.actor_id
        ))
        self.conn.commit()

    def delete_actor(self, actor_type: str, actor_id: str) -> None:
        """Delete an actor"""
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM actors WHERE actor_type = ? AND actor_id = ?",
            (actor_type, actor_id)
        )
        self.conn.commit()

    def list_actors(self) -> List[Actor]:
        """List all actors"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM actors")
        rows = cursor.fetchall()
        
        return [
            Actor(
                actor_type=row['actor_type'],
                actor_id=row['actor_id'],
                description=row['description'],
                state=json.loads(row['state']) if row['state'] else {},
                parent_actor=json.loads(row['parent_actor']) if row['parent_actor'] else None,
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            for row in rows
        ]

    # TargetMCP CRUD operations
    def create_target_mcp(self, target_mcp: TargetMCP) -> None:
        """Create a new target MCP"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO target_mcps (id, name, url, config, schema, actor_fields, example_data, connected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            target_mcp.id,
            target_mcp.name,
            target_mcp.url,
            json.dumps(target_mcp.config),
            json.dumps(target_mcp.schema),
            json.dumps(target_mcp.actor_fields),
            json.dumps(target_mcp.example_data),
            1 if target_mcp.connected else 0
        ))
        self.conn.commit()

    def get_target_mcp(self, target_id: str) -> Optional[TargetMCP]:
        """Get target MCP by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM target_mcps WHERE id = ?", (target_id,))
        row = cursor.fetchone()
        
        if row:
            return TargetMCP(
                id=row['id'],
                name=row['name'],
                url=row['url'],
                config=json.loads(row['config']) if row['config'] else {},
                schema=json.loads(row['schema']) if row['schema'] else {},
                actor_fields=json.loads(row['actor_fields']) if row['actor_fields'] else [],
                example_data=json.loads(row['example_data']) if row['example_data'] else {},
                connected=bool(row['connected'])
            )
        return None

    def update_target_mcp(self, target_mcp: TargetMCP) -> None:
        """Update an existing target MCP"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE target_mcps
            SET name = ?, url = ?, config = ?, schema = ?, actor_fields = ?, example_data = ?, connected = ?
            WHERE id = ?
        """, (
            target_mcp.name,
            target_mcp.url,
            json.dumps(target_mcp.config),
            json.dumps(target_mcp.schema),
            json.dumps(target_mcp.actor_fields),
            json.dumps(target_mcp.example_data),
            1 if target_mcp.connected else 0,
            target_mcp.id
        ))
        self.conn.commit()

    def delete_target_mcp(self, target_id: str) -> None:
        """Delete a target MCP"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM target_mcps WHERE id = ?", (target_id,))
        self.conn.commit()

    def list_target_mcps(self) -> List[TargetMCP]:
        """List all target MCPs"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM target_mcps")
        rows = cursor.fetchall()
        
        return [
            TargetMCP(
                id=row['id'],
                name=row['name'],
                url=row['url'],
                config=json.loads(row['config']) if row['config'] else {},
                schema=json.loads(row['schema']) if row['schema'] else {},
                actor_fields=json.loads(row['actor_fields']) if row['actor_fields'] else [],
                example_data=json.loads(row['example_data']) if row['example_data'] else {},
                connected=bool(row['connected'])
            )
            for row in rows
        ]

    # CausalityRelation CRUD operations
    def create_causality_relation(self, relation: CausalityRelation) -> int:
        """Create a new causality relation
        
        Returns:
            The ID of the created relation
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO causality_relations (cause_actor, cause_event, effect_actor, effect_event, time_delay, strength)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            relation.cause_actor,
            relation.cause_event,
            relation.effect_actor,
            relation.effect_event,
            relation.time_delay,
            relation.strength
        ))
        self.conn.commit()
        return cursor.lastrowid

    def get_causality_relation(self, relation_id: int) -> Optional[CausalityRelation]:
        """Get causality relation by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM causality_relations WHERE id = ?", (relation_id,))
        row = cursor.fetchone()
        
        if row:
            return CausalityRelation(
                cause_actor=row['cause_actor'],
                cause_event=row['cause_event'],
                effect_actor=row['effect_actor'],
                effect_event=row['effect_event'],
                time_delay=row['time_delay'],
                strength=row['strength']
            )
        return None

    def delete_causality_relation(self, relation_id: int) -> None:
        """Delete a causality relation"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM causality_relations WHERE id = ?", (relation_id,))
        self.conn.commit()

    def list_causality_relations(self) -> List[CausalityRelation]:
        """List all causality relations"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM causality_relations")
        rows = cursor.fetchall()
        
        return [
            CausalityRelation(
                cause_actor=row['cause_actor'],
                cause_event=row['cause_event'],
                effect_actor=row['effect_actor'],
                effect_event=row['effect_event'],
                time_delay=row['time_delay'],
                strength=row['strength']
            )
            for row in rows
        ]

    # PlotNode CRUD operations
    def create_plot_node(self, node: PlotNode) -> None:
        """Create a new plot node"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO plot_nodes (id, actor, event, timestamp_offset, data_pattern, children)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            node.id,
            node.actor,
            node.event,
            node.timestamp_offset,
            json.dumps(node.data_pattern),
            json.dumps(node.children)
        ))
        self.conn.commit()

    def get_plot_node(self, node_id: str) -> Optional[PlotNode]:
        """Get plot node by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM plot_nodes WHERE id = ?", (node_id,))
        row = cursor.fetchone()
        
        if row:
            return PlotNode(
                id=row['id'],
                actor=row['actor'],
                event=row['event'],
                timestamp_offset=row['timestamp_offset'],
                data_pattern=json.loads(row['data_pattern']) if row['data_pattern'] else {},
                children=json.loads(row['children']) if row['children'] else []
            )
        return None

    def update_plot_node(self, node: PlotNode) -> None:
        """Update an existing plot node"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE plot_nodes
            SET actor = ?, event = ?, timestamp_offset = ?, data_pattern = ?, children = ?
            WHERE id = ?
        """, (
            node.actor,
            node.event,
            node.timestamp_offset,
            json.dumps(node.data_pattern),
            json.dumps(node.children),
            node.id
        ))
        self.conn.commit()

    def delete_plot_node(self, node_id: str) -> None:
        """Delete a plot node"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM plot_nodes WHERE id = ?", (node_id,))
        self.conn.commit()

    def list_plot_nodes(self) -> List[PlotNode]:
        """List all plot nodes"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM plot_nodes")
        rows = cursor.fetchall()
        
        return [
            PlotNode(
                id=row['id'],
                actor=row['actor'],
                event=row['event'],
                timestamp_offset=row['timestamp_offset'],
                data_pattern=json.loads(row['data_pattern']) if row['data_pattern'] else {},
                children=json.loads(row['children']) if row['children'] else []
            )
            for row in rows
        ]

    # WorkflowState operations
    def save_workflow_state(self, state: WorkflowState) -> None:
        """Save or update workflow state (singleton)"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO workflow_state (id, stage, data, history, plot_suggestions)
            VALUES (1, ?, ?, ?, ?)
        """, (
            state.stage,
            json.dumps(state.data),
            json.dumps(state.history),
            json.dumps(state.plot_suggestions)
        ))
        self.conn.commit()

    def get_workflow_state(self) -> Optional[WorkflowState]:
        """Get current workflow state"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM workflow_state WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            return WorkflowState(
                stage=row['stage'],
                data=json.loads(row['data']) if row['data'] else {},
                history=json.loads(row['history']) if row['history'] else [],
                plot_suggestions=json.loads(row['plot_suggestions']) if row['plot_suggestions'] else []
            )
        return None

    def clear_workflow_state(self) -> None:
        """Clear workflow state"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM workflow_state WHERE id = 1")
        self.conn.commit()

    def clear_all_data(self) -> None:
        """Clear all data from database (useful for testing)"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM scenarios")
        cursor.execute("DELETE FROM actors")
        cursor.execute("DELETE FROM target_mcps")
        cursor.execute("DELETE FROM causality_relations")
        cursor.execute("DELETE FROM plot_nodes")
        cursor.execute("DELETE FROM workflow_state")
        self.conn.commit()
