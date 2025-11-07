"""
Scenario Persistence Tools for FakeMCP

Provides MCP tools for saving and loading scenario configurations to/from files.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from fakemcp.database import Database
from fakemcp.scenario_manager import ScenarioManager


class PersistenceTools:
    """场景持久化工具集"""

    def __init__(self, database: Database):
        """Initialize persistence tools
        
        Args:
            database: Database instance for persistence
        """
        self.scenario_manager = ScenarioManager(database)
        self.db = database

    def save_scenario(
        self,
        filepath: str,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """保存场景配置到文件
        
        MCP Tool: save_scenario
        
        将当前场景配置（包括目标 MCP、角色、因果关系等）保存到 YAML 文件，
        以便后续重复使用相同的测试场景。
        
        Args:
            filepath: 文件路径（YAML 格式）
            scenario_id: 场景 ID（可选，如果不提供则保存最新场景）
            
        Returns:
            操作结果，包含 success, filepath 等字段
            
        Example:
            >>> tools.save_scenario(
            ...     filepath="scenarios/memory_leak.yaml",
            ...     scenario_id="scenario_abc123"
            ... )
            {
                'success': True,
                'filepath': 'scenarios/memory_leak.yaml',
                'scenarioId': 'scenario_abc123',
                'summary': {
                    'description': '模拟内存泄露场景',
                    'targetMcps': 2,
                    'actors': 3,
                    'causalityRelations': 2
                }
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
                                'Use set_scenario tool to create a new scenario',
                                'Provide a specific scenario_id to save'
                            ]
                        }
                    }
                # 获取最新的场景（按 updated_at 排序）
                scenario = max(scenarios, key=lambda s: s.updated_at)
                scenario_id = scenario.id
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
                            },
                            'suggestions': [
                                'Check if the scenario_id is correct',
                                'Use get_scenario_status to list available scenarios'
                            ]
                        }
                    }
            
            # 保存到文件
            success = self.scenario_manager.save_to_file(scenario_id, filepath)
            
            if not success:
                return {
                    'success': False,
                    'error': {
                        'type': 'SaveError',
                        'message': f'Failed to save scenario to file: {filepath}',
                        'details': {
                            'scenario_id': scenario_id,
                            'filepath': filepath
                        },
                        'suggestions': [
                            'Check if the directory exists and is writable',
                            'Verify the filepath is valid'
                        ]
                    }
                }
            
            # 获取摘要信息
            actors = self.db.list_actors()
            causality_relations = self.db.list_causality_relations()
            
            return {
                'success': True,
                'filepath': filepath,
                'scenarioId': scenario_id,
                'summary': {
                    'description': scenario.description,
                    'targetMcps': len(scenario.target_mcps),
                    'actors': len(actors),
                    'causalityRelations': len(causality_relations)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'SaveError',
                    'message': str(e),
                    'details': {
                        'scenario_id': scenario_id,
                        'filepath': filepath
                    },
                    'suggestions': [
                        'Check if the directory exists and is writable',
                        'Verify the filepath is valid',
                        'Ensure the scenario exists in the database'
                    ]
                }
            }

    def load_scenario(
        self,
        filepath: str
    ) -> Dict[str, Any]:
        """从文件加载场景配置
        
        MCP Tool: load_scenario
        
        从 YAML 文件加载场景配置，恢复完整的场景状态（包括目标 MCP、
        角色、因果关系等）。加载后的场景可以立即用于生成模拟数据。
        
        Args:
            filepath: 文件路径（YAML 格式）
            
        Returns:
            操作结果，包含 success, scenarioId, summary 等字段
            
        Example:
            >>> tools.load_scenario(
            ...     filepath="scenarios/memory_leak.yaml"
            ... )
            {
                'success': True,
                'scenarioId': 'scenario_abc123',
                'summary': {
                    'description': '模拟内存泄露场景',
                    'targetMcps': 2,
                    'actors': 3,
                    'causalityRelations': 2,
                    'createdAt': '2024-01-01T10:00:00',
                    'updatedAt': '2024-01-01T12:00:00'
                }
            }
        """
        try:
            # 检查文件是否存在
            if not Path(filepath).exists():
                raise FileNotFoundError(f'File not found: {filepath}')
            
            # 从文件加载
            scenario = self.scenario_manager.load_from_file(filepath)
            
            if not scenario:
                return {
                    'success': False,
                    'error': {
                        'type': 'LoadError',
                        'message': f'Failed to load scenario from file: {filepath}',
                        'details': {
                            'filepath': filepath
                        },
                        'suggestions': [
                            'Verify the file is a valid YAML file',
                            'Ensure the file contains a valid scenario configuration'
                        ]
                    }
                }
            
            # 获取摘要信息
            actors = self.db.list_actors()
            causality_relations = self.db.list_causality_relations()
            
            # 计算实际存在的 target MCPs 数量
            actual_target_mcps = 0
            for target_id in scenario.target_mcps:
                if self.db.get_target_mcp(target_id):
                    actual_target_mcps += 1
            
            return {
                'success': True,
                'scenarioId': scenario.id,
                'summary': {
                    'description': scenario.description,
                    'targetMcps': actual_target_mcps,
                    'actors': len(actors),
                    'causalityRelations': len(causality_relations),
                    'createdAt': scenario.created_at.isoformat(),
                    'updatedAt': scenario.updated_at.isoformat()
                }
            }
            
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': {
                    'type': 'FileNotFoundError',
                    'message': f'File not found: {filepath}',
                    'details': {
                        'filepath': filepath
                    },
                    'suggestions': [
                        'Check if the filepath is correct',
                        'Verify the file exists'
                    ]
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'LoadError',
                    'message': str(e),
                    'details': {
                        'filepath': filepath
                    },
                    'suggestions': [
                        'Check if the file is a valid YAML file',
                        'Verify the file contains a valid scenario configuration',
                        'Ensure the file is readable'
                    ]
                }
            }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """获取 MCP 工具定义
        
        Returns:
            工具定义列表，符合 MCP 协议格式
        """
        return [
            {
                'name': 'save_scenario',
                'description': '保存场景配置到 YAML 文件。包含所有目标服务器配置、角色定义和场景参数，以便后续重复使用。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'filepath': {
                            'type': 'string',
                            'description': '文件路径（YAML 格式），例如："scenarios/memory_leak.yaml"'
                        },
                        'scenario_id': {
                            'type': 'string',
                            'description': '场景 ID（可选，如果不提供则保存最新场景）'
                        }
                    },
                    'required': ['filepath']
                }
            },
            {
                'name': 'load_scenario',
                'description': '从 YAML 文件加载场景配置。恢复完整的场景状态，包括目标 MCP、角色、因果关系等。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'filepath': {
                            'type': 'string',
                            'description': '文件路径（YAML 格式），例如："scenarios/memory_leak.yaml"'
                        }
                    },
                    'required': ['filepath']
                }
            }
        ]
