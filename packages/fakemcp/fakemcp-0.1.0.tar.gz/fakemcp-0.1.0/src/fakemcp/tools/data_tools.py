"""
Data Operation Tools for FakeMCP

Provides MCP tools for fetching real data, generating mock data,
and validating mock data.
"""

from typing import Any, Dict, List, Optional

from fakemcp.database import Database
from fakemcp.data_generator import DataGenerator
from fakemcp.target_mcp_analyzer import TargetMCPAnalyzer
from fakemcp.validation_service import ValidationService


class DataTools:
    """数据操作工具集"""

    def __init__(self, database: Database):
        """Initialize data tools
        
        Args:
            database: Database instance for persistence
        """
        self.db = database
        self.target_mcp_analyzer = TargetMCPAnalyzer(database)
        self.data_generator = DataGenerator()
        self.validation_service = ValidationService()

    async def fetch_real_data(
        self,
        target_id: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """从真实 MCP 服务器获取示例数据
        
        MCP Tool: fetch_real_data
        
        Args:
            target_id: 目标 MCP ID
            tool_name: 工具名称
            parameters: 调用参数
            
        Returns:
            操作结果，包含 success, data, cached 等字段
            
        Example:
            >>> await tools.fetch_real_data(
            ...     target_id="prometheus",
            ...     tool_name="query_metrics",
            ...     parameters={"instance": "server-01", "metric": "memory_usage"}
            ... )
            {
                'success': True,
                'data': {...},
                'cached': False,
                'targetId': 'prometheus',
                'toolName': 'query_metrics'
            }
        """
        try:
            # 检查目标 MCP 是否存在
            target_mcp = self.db.get_target_mcp(target_id)
            if not target_mcp:
                return {
                    'success': False,
                    'error': {
                        'type': 'TargetMCPNotFoundError',
                        'message': f'Target MCP not found: {target_id}',
                        'details': {
                            'target_id': target_id
                        },
                        'suggestions': [
                            'Use add_target_mcp to add the target MCP server first',
                            'Check if the target_id is correct'
                        ]
                    }
                }
            
            # 检查工具是否存在
            tool_exists = False
            if target_mcp.schema and 'tools' in target_mcp.schema:
                tool_exists = any(
                    tool.get('name') == tool_name
                    for tool in target_mcp.schema['tools']
                )
            
            if not tool_exists:
                return {
                    'success': False,
                    'error': {
                        'type': 'ToolNotFoundError',
                        'message': f'Tool not found in target MCP: {tool_name}',
                        'details': {
                            'target_id': target_id,
                            'tool_name': tool_name,
                            'available_tools': [
                                tool.get('name')
                                for tool in target_mcp.schema.get('tools', [])
                            ] if target_mcp.schema else []
                        },
                        'suggestions': [
                            'Check the tool name spelling',
                            'Use get_scenario_status to see available tools'
                        ]
                    }
                }
            
            # 获取真实数据
            data = await self.target_mcp_analyzer.fetch_real_data(
                target_id=target_id,
                tool_name=tool_name,
                parameters=parameters
            )
            
            # 检查是否来自缓存
            cached = self.target_mcp_analyzer._get_cached_data(
                target_id, tool_name, parameters
            ) is not None
            
            return {
                'success': True,
                'data': data,
                'cached': cached,
                'targetId': target_id,
                'toolName': tool_name,
                'parameters': parameters
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'DataFetchError',
                    'message': str(e),
                    'details': {
                        'target_id': target_id,
                        'tool_name': tool_name,
                        'parameters': parameters
                    },
                    'suggestions': [
                        'Verify the target MCP server is running and accessible',
                        'Check if the parameters are correct',
                        'Ensure network connectivity to the target MCP'
                    ]
                }
            }

    def generate_mock_data(
        self,
        target_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """生成模拟数据
        
        MCP Tool: generate_mock_data
        
        Args:
            target_id: 目标 MCP ID
            tool_name: 工具名称
            parameters: 调用参数（包含角色信息）
            scenario_id: 场景 ID（可选，如果不提供则使用最新场景）
            
        Returns:
            操作结果，包含 success, data, actorsInvolved 等字段
            
        Example:
            >>> tools.generate_mock_data(
            ...     target_id="prometheus",
            ...     tool_name="query_metrics",
            ...     parameters={"instance": "server-01", "metric": "memory_usage"}
            ... )
            {
                'success': True,
                'data': {...},
                'actorsInvolved': ['server-01'],
                'targetId': 'prometheus',
                'toolName': 'query_metrics',
                'basedOnPlot': True
            }
        """
        try:
            # 获取目标 MCP
            target_mcp = self.db.get_target_mcp(target_id)
            if not target_mcp:
                return {
                    'success': False,
                    'error': {
                        'type': 'TargetMCPNotFoundError',
                        'message': f'Target MCP not found: {target_id}',
                        'details': {
                            'target_id': target_id
                        },
                        'suggestions': [
                            'Use add_target_mcp to add the target MCP server first'
                        ]
                    }
                }
            
            # 获取场景
            if scenario_id:
                scenario = self.db.get_scenario(scenario_id)
            else:
                scenarios = self.db.list_scenarios()
                if not scenarios:
                    return {
                        'success': False,
                        'error': {
                            'type': 'NoScenarioError',
                            'message': 'No scenario found. Please create a scenario first.',
                            'suggestions': [
                                'Use set_scenario to create a scenario'
                            ]
                        }
                    }
                # 获取最新场景
                scenario = max(scenarios, key=lambda s: s.updated_at)
            
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
            
            # 获取所有角色
            actors = self.db.list_actors()
            
            # 获取剧情图（如果存在）
            plot_graph = None
            if 'plot_graph' in scenario.metadata and scenario.metadata['plot_graph'] is not None:
                from fakemcp.plot_manager import PlotGraph
                plot_graph = PlotGraph.from_dict(scenario.metadata['plot_graph'])
            
            # 生成模拟数据
            data = self.data_generator.generate(
                target_mcp=target_mcp,
                tool_name=tool_name,
                parameters=parameters,
                actors=actors,
                scenario=scenario,
                plot_graph=plot_graph
            )
            
            # 识别涉及的角色
            actors_involved = []
            for field in target_mcp.actor_fields:
                if field in parameters:
                    actors_involved.append(parameters[field])
            
            return {
                'success': True,
                'data': data,
                'actorsInvolved': actors_involved,
                'targetId': target_id,
                'toolName': tool_name,
                'parameters': parameters,
                'basedOnPlot': plot_graph is not None,
                'scenarioId': scenario.id
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'DataGenerationError',
                    'message': str(e),
                    'details': {
                        'target_id': target_id,
                        'tool_name': tool_name,
                        'parameters': parameters
                    },
                    'suggestions': [
                        'Ensure actors are configured for the parameters',
                        'Check if the scenario is properly set up',
                        'Verify the tool name and parameters are correct'
                    ]
                }
            }

    def validate_mock_data(
        self,
        target_id: str,
        tool_name: str,
        mock_data: Any,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """验证模拟数据的合理性
        
        MCP Tool: validate_mock_data
        
        Args:
            target_id: 目标 MCP ID
            tool_name: 工具名称
            mock_data: 模拟数据
            scenario_id: 场景 ID（可选）
            
        Returns:
            验证结果，包含 valid, issues, suggestions 等字段
            
        Example:
            >>> tools.validate_mock_data(
            ...     target_id="prometheus",
            ...     tool_name="query_metrics",
            ...     mock_data={...}
            ... )
            {
                'valid': True,
                'issues': [],
                'suggestions': [],
                'targetId': 'prometheus',
                'toolName': 'query_metrics'
            }
        """
        try:
            # 获取目标 MCP
            target_mcp = self.db.get_target_mcp(target_id)
            if not target_mcp:
                return {
                    'valid': False,
                    'error': {
                        'type': 'TargetMCPNotFoundError',
                        'message': f'Target MCP not found: {target_id}',
                        'details': {
                            'target_id': target_id
                        }
                    }
                }
            
            # 获取场景
            if scenario_id:
                scenario = self.db.get_scenario(scenario_id)
            else:
                scenarios = self.db.list_scenarios()
                if not scenarios:
                    return {
                        'valid': False,
                        'error': {
                            'type': 'NoScenarioError',
                            'message': 'No scenario found for validation context'
                        }
                    }
                scenario = max(scenarios, key=lambda s: s.updated_at)
            
            if not scenario:
                return {
                    'valid': False,
                    'error': {
                        'type': 'ScenarioNotFoundError',
                        'message': f'Scenario not found: {scenario_id}'
                    }
                }
            
            # 验证数据
            validation_result = self.validation_service.validate_mock_data(
                mock_data=mock_data,
                target_mcp=target_mcp,
                tool_name=tool_name,
                scenario=scenario
            )
            
            # 生成修正建议
            if not validation_result['valid']:
                correction_suggestions = self.validation_service.generate_correction_suggestions(
                    validation_result,
                    context={
                        'target_id': target_id,
                        'tool_name': tool_name,
                        'scenario': scenario.description
                    }
                )
                validation_result['correctionSuggestions'] = correction_suggestions
            
            # 添加元数据
            validation_result['targetId'] = target_id
            validation_result['toolName'] = tool_name
            validation_result['scenarioId'] = scenario.id
            
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'error': {
                    'type': 'ValidationError',
                    'message': str(e),
                    'details': {
                        'target_id': target_id,
                        'tool_name': tool_name
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
                'name': 'fetch_real_data',
                'description': '从真实的目标 MCP 服务器获取示例数据。数据将被缓存并用于学习数据格式。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'target_id': {
                            'type': 'string',
                            'description': '目标 MCP 的 ID'
                        },
                        'tool_name': {
                            'type': 'string',
                            'description': '要调用的工具名称'
                        },
                        'parameters': {
                            'type': 'object',
                            'description': '工具调用参数（JSON 对象）'
                        }
                    },
                    'required': ['target_id', 'tool_name', 'parameters']
                }
            },
            {
                'name': 'generate_mock_data',
                'description': '根据角色配置和场景描述生成模拟数据。如果存在剧情图，将基于剧情生成数据。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'target_id': {
                            'type': 'string',
                            'description': '目标 MCP 的 ID'
                        },
                        'tool_name': {
                            'type': 'string',
                            'description': '要模拟的工具名称'
                        },
                        'parameters': {
                            'type': 'object',
                            'description': '调用参数（包含角色信息，如 instance, server_id 等）'
                        },
                        'scenario_id': {
                            'type': 'string',
                            'description': '场景 ID（可选，如果不提供则使用最新场景）'
                        }
                    },
                    'required': ['target_id', 'tool_name', 'parameters']
                }
            },
            {
                'name': 'validate_mock_data',
                'description': '验证模拟数据的合理性，包括 Schema 验证、逻辑一致性检查、时间戳验证等。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'target_id': {
                            'type': 'string',
                            'description': '目标 MCP 的 ID'
                        },
                        'tool_name': {
                            'type': 'string',
                            'description': '工具名称'
                        },
                        'mock_data': {
                            'description': '要验证的模拟数据（任意 JSON 类型）'
                        },
                        'scenario_id': {
                            'type': 'string',
                            'description': '场景 ID（可选）'
                        }
                    },
                    'required': ['target_id', 'tool_name', 'mock_data']
                }
            }
        ]
