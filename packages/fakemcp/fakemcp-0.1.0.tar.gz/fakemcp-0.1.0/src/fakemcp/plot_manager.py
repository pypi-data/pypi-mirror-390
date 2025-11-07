"""
Plot Manager for FakeMCP
Manages plot graphs, causality relations, and plot expansion prompts
"""

from typing import Any, Dict, List, Optional, Set, Tuple
import uuid

from fakemcp.database import Database
from fakemcp.models import CausalityRelation, PlotNode, Scenario


class PlotGraph:
    """Represents a plot graph with nodes and edges (causality relations)"""
    
    def __init__(self):
        self.nodes: Dict[str, PlotNode] = {}
        self.edges: List[CausalityRelation] = []
    
    def add_node(self, node: PlotNode) -> None:
        """Add a node to the graph"""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: CausalityRelation) -> None:
        """Add an edge (causality relation) to the graph"""
        self.edges.append(edge)
    
    def get_node(self, node_id: str) -> Optional[PlotNode]:
        """Get a node by ID"""
        return self.nodes.get(node_id)
    
    def get_outgoing_relations(self, actor_id: str) -> List[CausalityRelation]:
        """Get all causality relations where the given actor is the cause"""
        return [edge for edge in self.edges if edge.cause_actor == actor_id]
    
    def get_incoming_relations(self, actor_id: str) -> List[CausalityRelation]:
        """Get all causality relations where the given actor is the effect"""
        return [edge for edge in self.edges if edge.effect_actor == actor_id]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert plot graph to dictionary"""
        return {
            'nodes': [
                {
                    'id': node.id,
                    'actor': node.actor,
                    'event': node.event,
                    'timestamp_offset': node.timestamp_offset,
                    'data_pattern': node.data_pattern,
                    'children': node.children
                }
                for node in self.nodes.values()
            ],
            'edges': [
                {
                    'cause_actor': edge.cause_actor,
                    'cause_event': edge.cause_event,
                    'effect_actor': edge.effect_actor,
                    'effect_event': edge.effect_event,
                    'time_delay': edge.time_delay,
                    'strength': edge.strength
                }
                for edge in self.edges
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlotGraph':
        """Create a PlotGraph from a dictionary
        
        Args:
            data: Dictionary representation of the plot graph
            
        Returns:
            PlotGraph instance
        """
        plot_graph = cls()
        
        # Reconstruct nodes
        for node_data in data.get('nodes', []):
            node = PlotNode(
                id=node_data['id'],
                actor=node_data['actor'],
                event=node_data['event'],
                timestamp_offset=node_data['timestamp_offset'],
                data_pattern=node_data['data_pattern'],
                children=node_data['children']
            )
            plot_graph.add_node(node)
        
        # Reconstruct edges
        for edge_data in data.get('edges', []):
            edge = CausalityRelation(
                cause_actor=edge_data['cause_actor'],
                cause_event=edge_data['cause_event'],
                effect_actor=edge_data['effect_actor'],
                effect_event=edge_data['effect_event'],
                time_delay=edge_data['time_delay'],
                strength=edge_data['strength']
            )
            plot_graph.add_edge(edge)
        
        return plot_graph


class PlotManager:
    """Manages plot graphs, causality relations, and plot consistency"""
    
    def __init__(self, db: Database):
        """Initialize PlotManager
        
        Args:
            db: Database instance
        """
        self.db = db
    
    def add_causality_relation(self, relation: CausalityRelation) -> str:
        """Add a causality relation
        
        Args:
            relation: CausalityRelation to add
            
        Returns:
            Relation ID as string
        """
        relation_id = self.db.create_causality_relation(relation)
        return str(relation_id)

    def build_plot_graph(self, scenario: Optional[Scenario] = None) -> PlotGraph:
        """Build a plot graph from causality relations
        
        Args:
            scenario: Optional scenario to filter relations (currently not used)
            
        Returns:
            PlotGraph instance
        """
        plot_graph = PlotGraph()
        
        # Get all causality relations
        relations = self.db.list_causality_relations()
        
        # Build a map of actor+event to node
        node_map: Dict[str, PlotNode] = {}
        
        # Create nodes for all unique actor+event combinations
        for relation in relations:
            # Create cause node
            cause_key = f"{relation.cause_actor}:{relation.cause_event}"
            if cause_key not in node_map:
                node_id = str(uuid.uuid4())
                node = PlotNode(
                    id=node_id,
                    actor=relation.cause_actor,
                    event=relation.cause_event,
                    timestamp_offset=0,  # Will be calculated later
                    data_pattern={},
                    children=[]
                )
                node_map[cause_key] = node
                plot_graph.add_node(node)
            
            # Create effect node
            effect_key = f"{relation.effect_actor}:{relation.effect_event}"
            if effect_key not in node_map:
                node_id = str(uuid.uuid4())
                node = PlotNode(
                    id=node_id,
                    actor=relation.effect_actor,
                    event=relation.effect_event,
                    timestamp_offset=0,  # Will be calculated later
                    data_pattern={},
                    children=[]
                )
                node_map[effect_key] = node
                plot_graph.add_node(node)
            
            # Add edge
            plot_graph.add_edge(relation)
            
            # Update children relationship
            cause_node = node_map[cause_key]
            effect_node = node_map[effect_key]
            if effect_node.id not in cause_node.children:
                cause_node.children.append(effect_node.id)
        
        # Calculate timestamp offsets based on causality chain
        self._calculate_timestamp_offsets(plot_graph)
        
        return plot_graph
    
    def _calculate_timestamp_offsets(self, plot_graph: PlotGraph) -> None:
        """Calculate timestamp offsets for all nodes based on causality chain
        
        Args:
            plot_graph: PlotGraph to update
        """
        # Find root nodes (nodes with no incoming edges)
        root_nodes = []
        for node in plot_graph.nodes.values():
            incoming = plot_graph.get_incoming_relations(node.actor)
            # Check if this specific event has incoming relations
            has_incoming = any(
                rel.effect_actor == node.actor and rel.effect_event == node.event
                for rel in plot_graph.edges
            )
            if not has_incoming:
                root_nodes.append(node)
                node.timestamp_offset = 0
        
        # BFS to calculate offsets
        visited: Set[str] = set()
        queue = root_nodes.copy()
        
        while queue:
            current_node = queue.pop(0)
            if current_node.id in visited:
                continue
            visited.add(current_node.id)
            
            # Update children offsets based on outgoing relations from this specific event
            for relation in plot_graph.edges:
                if relation.cause_actor == current_node.actor and relation.cause_event == current_node.event:
                    # Find the effect node
                    for node in plot_graph.nodes.values():
                        if node.actor == relation.effect_actor and node.event == relation.effect_event:
                            # Update offset if this path gives a larger offset
                            new_offset = current_node.timestamp_offset + relation.time_delay
                            if new_offset > node.timestamp_offset:
                                node.timestamp_offset = new_offset
                            
                            if node not in queue:
                                queue.append(node)
                            break
    
    def validate_plot_consistency(self, plot_graph: Optional[PlotGraph] = None) -> Dict[str, Any]:
        """Validate plot consistency
        
        Args:
            plot_graph: Optional PlotGraph to validate. If None, builds from current relations.
            
        Returns:
            Dictionary with validation results
        """
        if plot_graph is None:
            plot_graph = self.build_plot_graph()
        
        issues = []
        
        # Check for circular dependencies
        circular_deps = self._detect_circular_dependencies(plot_graph)
        for cycle in circular_deps:
            issues.append({
                'type': 'circular_dependency',
                'description': f"Circular dependency detected: {' -> '.join(cycle)}",
                'affectedNodes': cycle
            })
        
        # Check for time conflicts
        time_conflicts = self._detect_time_conflicts(plot_graph)
        for conflict in time_conflicts:
            issues.append({
                'type': 'time_conflict',
                'description': conflict['description'],
                'affectedNodes': conflict['nodes']
            })
        
        # Check for missing actors
        missing_actors = self._detect_missing_actors(plot_graph)
        for actor in missing_actors:
            issues.append({
                'type': 'missing_actor',
                'description': f"Actor '{actor}' referenced in plot but not configured",
                'affectedNodes': [actor]
            })
        
        suggestions = []
        if circular_deps:
            suggestions.append("Remove one or more causality relations to break the circular dependency")
        if time_conflicts:
            suggestions.append("Adjust time delays to ensure proper event ordering")
        if missing_actors:
            suggestions.append("Add missing actors using add_actor_config tool")
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions
        }

    def _detect_circular_dependencies(self, plot_graph: PlotGraph) -> List[List[str]]:
        """Detect circular dependencies in the plot graph
        
        Args:
            plot_graph: PlotGraph to check
            
        Returns:
            List of cycles, where each cycle is a list of actor IDs
        """
        cycles = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []
        
        def dfs(actor: str) -> bool:
            """DFS to detect cycles"""
            visited.add(actor)
            rec_stack.add(actor)
            path.append(actor)
            
            # Check all outgoing relations
            outgoing = plot_graph.get_outgoing_relations(actor)
            for relation in outgoing:
                effect_actor = relation.effect_actor
                
                if effect_actor not in visited:
                    if dfs(effect_actor):
                        return True
                elif effect_actor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(effect_actor)
                    cycle = path[cycle_start:] + [effect_actor]
                    cycles.append(cycle)
                    return True
            
            path.pop()
            rec_stack.remove(actor)
            return False
        
        # Check all nodes
        all_actors = set()
        for node in plot_graph.nodes.values():
            all_actors.add(node.actor)
        
        for actor in all_actors:
            if actor not in visited:
                dfs(actor)
        
        return cycles
    
    def _detect_time_conflicts(self, plot_graph: PlotGraph) -> List[Dict[str, Any]]:
        """Detect time conflicts in the plot graph
        
        Args:
            plot_graph: PlotGraph to check
            
        Returns:
            List of time conflicts
        """
        conflicts = []
        
        # Check if any effect happens before its cause
        for relation in plot_graph.edges:
            cause_key = f"{relation.cause_actor}:{relation.cause_event}"
            effect_key = f"{relation.effect_actor}:{relation.effect_event}"
            
            cause_node = None
            effect_node = None
            
            for node in plot_graph.nodes.values():
                if node.actor == relation.cause_actor and node.event == relation.cause_event:
                    cause_node = node
                if node.actor == relation.effect_actor and node.event == relation.effect_event:
                    effect_node = node
            
            if cause_node and effect_node:
                expected_effect_time = cause_node.timestamp_offset + relation.time_delay
                if effect_node.timestamp_offset < expected_effect_time:
                    conflicts.append({
                        'description': f"Effect '{effect_key}' occurs before expected time based on cause '{cause_key}'",
                        'nodes': [cause_key, effect_key]
                    })
        
        return conflicts
    
    def _detect_missing_actors(self, plot_graph: PlotGraph) -> List[str]:
        """Detect actors referenced in plot but not configured
        
        Args:
            plot_graph: PlotGraph to check
            
        Returns:
            List of missing actor IDs
        """
        # Get all actors from plot
        plot_actors = set()
        for node in plot_graph.nodes.values():
            plot_actors.add(node.actor)
        
        # Get all configured actors
        configured_actors = set()
        for actor in self.db.list_actors():
            configured_actors.add(actor.actor_id)
        
        # Find missing actors
        missing = plot_actors - configured_actors
        return list(missing)
    
    def get_timeline(self, plot_graph: Optional[PlotGraph] = None) -> List[Dict[str, Any]]:
        """Generate a timeline from the plot graph
        
        Args:
            plot_graph: Optional PlotGraph. If None, builds from current relations.
            
        Returns:
            List of timeline events sorted by timestamp
        """
        if plot_graph is None:
            plot_graph = self.build_plot_graph()
        
        # Group events by timestamp
        timeline_map: Dict[int, List[str]] = {}
        
        for node in plot_graph.nodes.values():
            timestamp = node.timestamp_offset
            event_key = f"{node.actor}:{node.event}"
            
            if timestamp not in timeline_map:
                timeline_map[timestamp] = []
            timeline_map[timestamp].append(event_key)
        
        # Convert to sorted list
        timeline = []
        for timestamp in sorted(timeline_map.keys()):
            timeline.append({
                'timestamp': timestamp,
                'events': timeline_map[timestamp]
            })
        
        return timeline

    def generate_plot_expansion_prompt(
        self,
        actor_id: str,
        event: str,
        scenario: Scenario
    ) -> Dict[str, Any]:
        """Generate a plot expansion prompt for AI IDE
        
        Args:
            actor_id: Current actor ID
            event: Current event description
            scenario: Current scenario
            
        Returns:
            Dictionary with prompt and context for AI IDE
        """
        # Get current actors
        current_actors = [actor.actor_id for actor in self.db.list_actors()]
        
        # Get target MCPs
        target_mcps = scenario.target_mcps
        
        # Get existing causality relations for context
        existing_relations = self.db.list_causality_relations()
        existing_relations_text = ""
        if existing_relations:
            existing_relations_text = "\n\n已有的因果关系:\n"
            for rel in existing_relations:
                existing_relations_text += f"- {rel.cause_actor}:{rel.cause_event} → {rel.effect_actor}:{rel.effect_event} (延迟: {rel.time_delay}秒)\n"
        
        # Build the prompt
        prompt = f"""基于以下场景，请分析可能的剧情扩展：

场景描述: {scenario.description}
当前事件: {actor_id} - {event}
已有角色: {', '.join(current_actors)}
可用的目标 MCP: {', '.join(target_mcps)}{existing_relations_text}

请提供 3-5 个剧情扩展建议，每个建议包括：
1. 类型: root_cause（根本原因）、side_effect（副作用）或 related_event（相关事件）
2. 描述: 简短的剧情描述
3. 涉及的角色: 可以是已有角色或新角色
4. 因果关系: 如果是因果关系，说明原因和结果
5. 时间延迟: 如果有因果关系，估计时间延迟（秒）

示例格式:
- [根本原因] server-02 的错误请求导致 server-01 内存泄露
  涉及: server-02 → server-01
  时间延迟: 300秒
  
- [副作用] server-01 内存泄露导致响应变慢
  涉及: server-01 (内存泄露) → server-01 (响应变慢)
  时间延迟: 600秒
  
- [根本原因] 数据库连接池未释放导致内存泄露
  涉及: 新角色 database-01 → server-01
  时间延迟: 60秒

请提供你的建议："""
        
        # Example format for AI to follow
        example_format = {
            "suggestions": [
                {
                    "type": "root_cause | side_effect | related_event",
                    "description": "剧情描述",
                    "cause_actor": "原因角色ID",
                    "cause_event": "原因事件",
                    "effect_actor": "结果角色ID",
                    "effect_event": "结果事件",
                    "time_delay": 300,
                    "is_new_actor": False
                }
            ]
        }
        
        return {
            'promptForAI': prompt,
            'currentActors': current_actors,
            'targetMcps': target_mcps,
            'exampleFormat': example_format
        }
