"""
Scenario and Target MCP Management Tools for FakeMCP

Provides MCP tools for managing scenarios and target MCP servers.
"""

from typing import Any, Dict, List, Optional

from fakemcp.database import Database
from fakemcp.scenario_manager import ScenarioManager
from fakemcp.target_mcp_analyzer import TargetMCPAnalyzer


class ScenarioTools:
    """场景和目标 MCP 管理工具集"""

    def __init__(self, database: Database):
        """Initialize scenario tools
        
        Args:
            database: Database instance for persistence
        """
        self.scenario_manager = ScenarioManager(database)
        self.target_mcp_analyzer = TargetMCPAnalyzer(database)
        self.db = database

    async def set_scenario(
        self,
        description: str,
        target_mcps: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """设置场景描述
        
        MCP Tool: set_scenario
        
        Args:
            description: 场景描述（自然语言）
            target_mcps: 涉及的目标 MCP IDs（可选）
            
        Returns:
            操作结果，包含 success, scenarioId, extractedActors 等字段
            
        Example:
            >>> await tools.set_scenario(
            ...     description="模拟内存泄露场景",
            ...     target_mcps=["prometheus", "cloudmonitoring"]
            ... )
            {
                'success': True,
                'scenarioId': 'scenario_abc123',
                'description': '模拟内存泄露场景',
                'extractedActors': [],
                'keywords': ['内存', '泄露', '场景', '模拟']
            }
        """
        try:
            # 创建场景
            scenario = self.scenario_manager.create_scenario(
                description=description,
                target_mcps=target_mcps or []
            )
            
            return {
                'success': True,
                'scenarioId': scenario.id,
                'description': scenario.description,
                'extractedActors': scenario.metadata.get('extracted_actors', []),
                'keywords': scenario.metadata.get('keywords', []),
                'targetMcps': scenario.target_mcps
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'ScenarioCreationError',
                    'message': str(e),
                    'details': {
                        'description': description
                    }
                }
            }

    async def add_target_mcp(
        self,
        name: str,
        url: str,
        config: Optional[Dict[str, Any]] = None,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """添加要模拟的目标 MCP 服务器
        
        MCP Tool: add_target_mcp
        
        Args:
            name: 目标 MCP 的名称
            url: 目标 MCP 的 URL
            config: 连接配置（认证等，可选）
            scenario_id: 要关联的场景 ID（可选）
            
        Returns:
            操作结果，包含 success, targetId, schema, detectedActorFields 等字段
            
        Example:
            >>> await tools.add_target_mcp(
            ...     name="Prometheus",
            ...     url="http://localhost:9090/mcp",
            ...     config={"auth_token": "xxx"}
            ... )
            {
                'success': True,
                'targetId': 'prometheus',
                'name': 'Prometheus',
                'url': 'http://localhost:9090/mcp',
                'schema': {...},
                'detectedActorFields': ['instance', 'job', 'server_id'],
                'connected': True
            }
        """
        try:
            # 生成 target_id（基于名称）
            target_id = name.lower().replace(' ', '_').replace('-', '_')
            
            # 连接到目标 MCP 并获取 Schema
            target_mcp = await self.target_mcp_analyzer.connect(
                target_id=target_id,
                name=name,
                url=url,
                config=config or {}
            )
            
            # 如果提供了 scenario_id，将此 target 添加到场景
            if scenario_id:
                scenario = self.scenario_manager.get_scenario(scenario_id)
                if scenario:
                    if target_id not in scenario.target_mcps:
                        scenario.target_mcps.append(target_id)
                        self.scenario_manager.update_scenario(
                            scenario_id,
                            target_mcps=scenario.target_mcps
                        )
            
            return {
                'success': True,
                'targetId': target_mcp.id,
                'name': target_mcp.name,
                'url': target_mcp.url,
                'schema': target_mcp.schema,
                'detectedActorFields': target_mcp.actor_fields,
                'connected': target_mcp.connected
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'TargetMCPConnectionError',
                    'message': str(e),
                    'details': {
                        'name': name,
                        'url': url
                    },
                    'suggestions': [
                        'Verify the URL is correct and the MCP server is running',
                        'Check network connectivity',
                        'Ensure authentication credentials are valid if required'
                    ]
                }
            }

    def get_scenario_status(
        self,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取当前场景状态
        
        MCP Tool: get_scenario_status
        
        Args:
            scenario_id: 场景 ID（可选，如果不提供则返回最新场景）
            
        Returns:
            场景状态信息
            
        Example:
            >>> tools.get_scenario_status(scenario_id="scenario_abc123")
            {
                'success': True,
                'scenarioId': 'scenario_abc123',
                'description': '模拟内存泄露场景',
                'targetMcps': [
                    {
                        'id': 'prometheus',
                        'name': 'Prometheus',
                        'url': 'http://localhost:9090/mcp',
                        'connected': True,
                        'actorFields': ['instance', 'job']
                    }
                ],
                'actors': 2,
                'causalityRelations': 1,
                'ready': True
            }
        """
        try:
            # 如果没有提供 scenario_id，获取最新的场景
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
                # 获取最新的场景（按 updated_at 排序）
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
            
            # 获取目标 MCP 信息
            target_mcps_info = []
            for target_id in scenario.target_mcps:
                target_mcp = self.db.get_target_mcp(target_id)
                if target_mcp:
                    target_mcps_info.append({
                        'id': target_mcp.id,
                        'name': target_mcp.name,
                        'url': target_mcp.url,
                        'connected': target_mcp.connected,
                        'actorFields': target_mcp.actor_fields
                    })
            
            # 获取角色数量
            actors = self.db.list_actors()
            actor_count = len(actors)
            
            # 获取因果关系数量
            causality_relations = self.db.list_causality_relations()
            causality_count = len(causality_relations)
            
            # 判断场景是否准备就绪
            # 准备就绪的条件：至少有一个目标 MCP 且至少有一个角色
            ready = len(target_mcps_info) > 0 and actor_count > 0
            
            return {
                'success': True,
                'scenarioId': scenario.id,
                'description': scenario.description,
                'targetMcps': target_mcps_info,
                'actors': actor_count,
                'causalityRelations': causality_count,
                'keywords': scenario.metadata.get('keywords', []),
                'ready': ready,
                'createdAt': scenario.created_at.isoformat(),
                'updatedAt': scenario.updated_at.isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'ScenarioStatusError',
                    'message': str(e),
                    'details': {
                        'scenario_id': scenario_id
                    }
                }
            }

    async def close(self):
        """关闭资源（如 HTTP 客户端）"""
        await self.target_mcp_analyzer.close()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取 MCP 工具定义
        
        Returns:
            工具定义列表，符合 MCP 协议格式
        """
        return [
            {
                'name': 'set_scenario',
                'description': '设置测试场景描述。FakeMCP 将解析场景描述并提取关键要素。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'description': {
                            'type': 'string',
                            'description': '场景描述（自然语言），例如："模拟内存泄露场景"'
                        },
                        'target_mcps': {
                            'type': 'array',
                            'description': '涉及的目标 MCP IDs（可选）',
                            'items': {
                                'type': 'string'
                            }
                        }
                    },
                    'required': ['description']
                }
            },
            {
                'name': 'add_target_mcp',
                'description': '添加要模拟的目标 MCP 服务器。FakeMCP 将连接到真实服务器获取 Schema 并识别角色字段。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string',
                            'description': '目标 MCP 的名称，例如："Prometheus"'
                        },
                        'url': {
                            'type': 'string',
                            'description': '目标 MCP 的 URL，例如："http://localhost:9090/mcp"'
                        },
                        'config': {
                            'type': 'object',
                            'description': '连接配置（认证等，可选）',
                            'properties': {
                                'auth_token': {
                                    'type': 'string',
                                    'description': '认证令牌'
                                }
                            }
                        },
                        'scenario_id': {
                            'type': 'string',
                            'description': '要关联的场景 ID（可选）'
                        }
                    },
                    'required': ['name', 'url']
                }
            },
            {
                'name': 'get_scenario_status',
                'description': '获取当前场景的状态信息，包括目标 MCP、角色数量、因果关系等。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'scenario_id': {
                            'type': 'string',
                            'description': '场景 ID（可选，如果不提供则返回最新场景）'
                        }
                    }
                }
            }
        ]
