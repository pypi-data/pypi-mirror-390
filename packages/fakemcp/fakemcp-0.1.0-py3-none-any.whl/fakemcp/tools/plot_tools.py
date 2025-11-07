"""
Plot Management Tools for FakeMCP

Provides MCP tools for managing plot graphs, causality relations, and plot expansion.
"""

from typing import Any, Dict, List, Optional

from fakemcp.database import Database
from fakemcp.models import CausalityRelation, Scenario
from fakemcp.plot_manager import PlotManager
from fakemcp.scenario_manager import ScenarioManager


class PlotTools:
    """剧情管理工具集"""

    def __init__(self, database: Database):
        """Initialize plot tools
        
        Args:
            database: Database instance for persistence
        """
        self.plot_manager = PlotManager(database)
        self.scenario_manager = ScenarioManager(database)
        self.db = database

    def request_plot_expansion(
        self,
        actor_id: str,
        event: str,
        context: Optional[Dict[str, Any]] = None,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """请求剧情扩展（返回提示词给 AI IDE）
        
        MCP Tool: request_plot_expansion
        
        Args:
            actor_id: 当前角色 ID
            event: 当前事件描述
            context: 当前场景上下文（可选）
            scenario_id: 场景 ID（可选，如果不提供则使用最新场景）
            
        Returns:
            包含 AI 提示词和上下文信息的字典
            
        Example:
            >>> tools.request_plot_expansion(
            ...     actor_id="server-01",
            ...     event="内存泄露"
            ... )
            {
                'success': True,
                'promptForAI': '基于以下场景，请分析可能的剧情扩展...',
                'currentActors': ['server-01', 'server-02'],
                'targetMcps': ['prometheus', 'cloudmonitoring'],
                'exampleFormat': {...}
            }
        """
        try:
            # 获取场景
            if not scenario_id:
                scenarios = self.scenario_manager.list_scenarios()
                if not scenarios:
                    return {
                        'success': False,
                        'error': {
                            'type': 'NoScenarioError',
                            'message': 'No scenario found. Please create a scenario first using set_scenario.',
                            'suggestions': [
                                'Use set_scenario tool to create a new scenario'
                            ]
                        }
                    }
                scenario = max(scenarios, key=lambda s: s.updated_at)
            else:
                scenario = self.scenario_manager.get_scenario(scenario_id)
                if not scenario:
                    return {
                        'success': False,
                        'error': {
                            'type': 'ScenarioNotFoundError',
                            'message': f'Scenario not found: {scenario_id}',
                            'details': {
                                'scenario_id': scenario_id
                            }
                        }
                    }
            
            # 生成剧情扩展提示词
            result = self.plot_manager.generate_plot_expansion_prompt(
                actor_id=actor_id,
                event=event,
                scenario=scenario
            )
            
            return {
                'success': True,
                **result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'PlotExpansionError',
                    'message': str(e),
                    'details': {
                        'actor_id': actor_id,
                        'event': event
                    }
                }
            }

    def add_causality_relation(
        self,
        cause_actor: str,
        cause_event: str,
        effect_actor: str,
        effect_event: str,
        time_delay: Optional[int] = None,
        strength: Optional[float] = None
    ) -> Dict[str, Any]:
        """添加因果关系
        
        MCP Tool: add_causality_relation
        
        Args:
            cause_actor: 原因角色 ID
            cause_event: 原因事件描述
            effect_actor: 结果角色 ID
            effect_event: 结果事件描述
            time_delay: 时间延迟（秒，默认 0）
            strength: 因果强度 (0-1，默认 1.0)
            
        Returns:
            操作结果，包含 success, relationId, plotUpdated 等字段
            
        Example:
            >>> tools.add_causality_relation(
            ...     cause_actor="server-02",
            ...     cause_event="错误请求增加",
            ...     effect_actor="server-01",
            ...     effect_event="内存泄露",
            ...     time_delay=300,
            ...     strength=0.9
            ... )
            {
                'success': True,
                'relationId': 'rel_123',
                'plotUpdated': True,
                'causeActor': 'server-02',
                'causeEvent': '错误请求增加',
                'effectActor': 'server-01',
                'effectEvent': '内存泄露',
                'timeDelay': 300,
                'strength': 0.9
            }
        """
        try:
            # 创建因果关系对象
            relation = CausalityRelation(
                cause_actor=cause_actor,
                cause_event=cause_event,
                effect_actor=effect_actor,
                effect_event=effect_event,
                time_delay=time_delay if time_delay is not None else 0,
                strength=strength if strength is not None else 1.0
            )
            
            # 添加到数据库
            relation_id = self.plot_manager.add_causality_relation(relation)
            
            return {
                'success': True,
                'relationId': relation_id,
                'plotUpdated': True,
                'causeActor': cause_actor,
                'causeEvent': cause_event,
                'effectActor': effect_actor,
                'effectEvent': effect_event,
                'timeDelay': relation.time_delay,
                'strength': relation.strength
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'CausalityRelationError',
                    'message': str(e),
                    'details': {
                        'cause_actor': cause_actor,
                        'cause_event': cause_event,
                        'effect_actor': effect_actor,
                        'effect_event': effect_event
                    },
                    'suggestions': [
                        'Ensure both actors exist in the scenario',
                        'Check that the event descriptions are meaningful',
                        'Verify time_delay is a positive integer',
                        'Verify strength is between 0 and 1'
                    ]
                }
            }

    def build_plot_graph(
        self,
        root_event: Optional[str] = None,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """构建剧情图
        
        MCP Tool: build_plot_graph
        
        Args:
            root_event: 可选的根事件，不提供则自动分析
            scenario_id: 场景 ID（可选）
            
        Returns:
            剧情图结构，包含节点和边
            
        Example:
            >>> tools.build_plot_graph()
            {
                'success': True,
                'plotGraph': {
                    'nodes': [
                        {
                            'id': 'node_123',
                            'actor': 'server-01',
                            'event': '内存泄露',
                            'timestamp_offset': 300,
                            'data_pattern': {},
                            'children': ['node_456']
                        }
                    ],
                    'edges': [
                        {
                            'cause_actor': 'server-02',
                            'cause_event': '错误请求',
                            'effect_actor': 'server-01',
                            'effect_event': '内存泄露',
                            'time_delay': 300,
                            'strength': 1.0
                        }
                    ]
                },
                'timeline': [
                    {
                        'timestamp': 0,
                        'events': ['server-02:错误请求']
                    },
                    {
                        'timestamp': 300,
                        'events': ['server-01:内存泄露']
                    }
                ]
            }
        """
        try:
            # 获取场景（如果需要）
            scenario = None
            if scenario_id:
                scenario = self.scenario_manager.get_scenario(scenario_id)
                if not scenario:
                    return {
                        'success': False,
                        'error': {
                            'type': 'ScenarioNotFoundError',
                            'message': f'Scenario not found: {scenario_id}',
                            'details': {
                                'scenario_id': scenario_id
                            }
                        }
                    }
            
            # 构建剧情图
            plot_graph = self.plot_manager.build_plot_graph(scenario)
            
            # 生成时间线
            timeline = self.plot_manager.get_timeline(plot_graph)
            
            return {
                'success': True,
                'plotGraph': plot_graph.to_dict(),
                'timeline': timeline,
                'nodeCount': len(plot_graph.nodes),
                'edgeCount': len(plot_graph.edges)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'PlotGraphBuildError',
                    'message': str(e),
                    'details': {
                        'root_event': root_event,
                        'scenario_id': scenario_id
                    },
                    'suggestions': [
                        'Ensure causality relations have been added',
                        'Check that all actors referenced in relations exist'
                    ]
                }
            }

    def validate_plot_consistency(
        self,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证剧情一致性
        
        MCP Tool: validate_plot_consistency
        
        Args:
            scenario_id: 场景 ID（可选）
            
        Returns:
            验证结果，包含一致性状态、问题列表和修正建议
            
        Example:
            >>> tools.validate_plot_consistency()
            {
                'success': True,
                'consistent': True,
                'issues': [],
                'suggestions': []
            }
            
            或者如果有问题：
            {
                'success': True,
                'consistent': False,
                'issues': [
                    {
                        'type': 'circular_dependency',
                        'description': 'Circular dependency detected: server-01 -> server-02 -> server-01',
                        'affectedNodes': ['server-01', 'server-02', 'server-01']
                    }
                ],
                'suggestions': [
                    'Remove one or more causality relations to break the circular dependency'
                ]
            }
        """
        try:
            # 获取场景（如果需要）
            scenario = None
            if scenario_id:
                scenario = self.scenario_manager.get_scenario(scenario_id)
                if not scenario:
                    return {
                        'success': False,
                        'error': {
                            'type': 'ScenarioNotFoundError',
                            'message': f'Scenario not found: {scenario_id}',
                            'details': {
                                'scenario_id': scenario_id
                            }
                        }
                    }
            
            # 验证剧情一致性
            validation_result = self.plot_manager.validate_plot_consistency()
            
            return {
                'success': True,
                **validation_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'PlotValidationError',
                    'message': str(e),
                    'details': {
                        'scenario_id': scenario_id
                    }
                }
            }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取 MCP 工具定义
        
        Returns:
            工具定义列表，符合 MCP 协议格式
        """
        return [
            {
                'name': 'request_plot_expansion',
                'description': '请求剧情扩展建议。返回精心设计的提示词给 AI IDE，让 AI 分析并生成剧情扩展建议（如根本原因、副作用、相关事件）。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'actor_id': {
                            'type': 'string',
                            'description': '当前角色 ID，例如："server-01"'
                        },
                        'event': {
                            'type': 'string',
                            'description': '当前事件描述，例如："内存泄露"'
                        },
                        'context': {
                            'type': 'object',
                            'description': '当前场景上下文（可选）'
                        },
                        'scenario_id': {
                            'type': 'string',
                            'description': '场景 ID（可选，如果不提供则使用最新场景）'
                        }
                    },
                    'required': ['actor_id', 'event']
                }
            },
            {
                'name': 'add_causality_relation',
                'description': '添加因果关系。定义一个事件如何导致另一个事件，包括时间延迟和因果强度。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'cause_actor': {
                            'type': 'string',
                            'description': '原因角色 ID，例如："server-02"'
                        },
                        'cause_event': {
                            'type': 'string',
                            'description': '原因事件描述，例如："错误请求增加"'
                        },
                        'effect_actor': {
                            'type': 'string',
                            'description': '结果角色 ID，例如："server-01"'
                        },
                        'effect_event': {
                            'type': 'string',
                            'description': '结果事件描述，例如："内存泄露"'
                        },
                        'time_delay': {
                            'type': 'integer',
                            'description': '时间延迟（秒），默认 0',
                            'default': 0
                        },
                        'strength': {
                            'type': 'number',
                            'description': '因果强度 (0-1)，默认 1.0',
                            'default': 1.0,
                            'minimum': 0,
                            'maximum': 1
                        }
                    },
                    'required': ['cause_actor', 'cause_event', 'effect_actor', 'effect_event']
                }
            },
            {
                'name': 'build_plot_graph',
                'description': '构建剧情图。基于已添加的因果关系构建完整的剧情图，包括节点、边和时间线。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'root_event': {
                            'type': 'string',
                            'description': '可选的根事件，不提供则自动分析'
                        },
                        'scenario_id': {
                            'type': 'string',
                            'description': '场景 ID（可选）'
                        }
                    }
                }
            },
            {
                'name': 'validate_plot_consistency',
                'description': '验证剧情一致性。检查剧情图中的循环依赖、时间冲突和缺失角色等问题。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'scenario_id': {
                            'type': 'string',
                            'description': '场景 ID（可选）'
                        }
                    }
                }
            }
        ]
