"""
Actor Management Tools for FakeMCP

Provides MCP tools for managing actors (roles) in test scenarios.
"""

from typing import Any, Dict, List, Optional

from fakemcp.actor_manager import ActorManager
from fakemcp.database import Database


class ActorTools:
    """角色管理工具集"""

    def __init__(self, database: Database):
        """Initialize actor tools
        
        Args:
            database: Database instance for persistence
        """
        self.actor_manager = ActorManager(database)

    def add_actor_config(
        self,
        actor_type: str,
        actor_id: str,
        description: str,
        parent_actor: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """为角色添加场景配置
        
        MCP Tool: add_actor_config
        
        Args:
            actor_type: 角色类型（如 'city', 'server_id', 'user_id'）
            actor_id: 角色实例（如 '深圳', 'server-01', 'user-001'）
            description: 该角色的场景描述
            parent_actor: 可选的父级角色，格式: {'actor_type': 'city', 'actor_id': '深圳'}
            
        Returns:
            操作结果，包含 success, actorKey, inheritedFrom 等字段
            
        Example:
            >>> tools.add_actor_config(
            ...     actor_type='server_id',
            ...     actor_id='server-01',
            ...     description='内存持续增长，从 2GB 增长到 8GB'
            ... )
            {
                'success': True,
                'actorKey': 'server_id:server-01',
                'actor': {
                    'actor_type': 'server_id',
                    'actor_id': 'server-01',
                    'description': '内存持续增长，从 2GB 增长到 8GB',
                    'state': {},
                    'parent_actor': None,
                    'metadata': {...}
                }
            }
        """
        try:
            actor = self.actor_manager.add_actor(
                actor_type=actor_type,
                actor_id=actor_id,
                description=description,
                parent_actor=parent_actor
            )
            
            actor_key = f"{actor_type}:{actor_id}"
            
            result = {
                'success': True,
                'actorKey': actor_key,
                'actor': {
                    'actor_type': actor.actor_type,
                    'actor_id': actor.actor_id,
                    'description': actor.description,
                    'state': actor.state,
                    'parent_actor': actor.parent_actor,
                    'metadata': actor.metadata
                }
            }
            
            # 如果有父级角色，添加继承信息
            if parent_actor:
                parent_key = f"{parent_actor['actor_type']}:{parent_actor['actor_id']}"
                result['inheritedFrom'] = parent_key
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'ActorConfigError',
                    'message': str(e),
                    'details': {
                        'actor_type': actor_type,
                        'actor_id': actor_id
                    }
                }
            }

    def remove_actor_config(
        self,
        actor_type: str,
        actor_id: str
    ) -> Dict[str, Any]:
        """删除角色配置
        
        MCP Tool: remove_actor_config
        
        Args:
            actor_type: 角色类型
            actor_id: 角色实例
            
        Returns:
            操作结果，包含 success 和 removed 字段
            
        Example:
            >>> tools.remove_actor_config(
            ...     actor_type='server_id',
            ...     actor_id='server-01'
            ... )
            {
                'success': True,
                'removed': True,
                'actorKey': 'server_id:server-01'
            }
        """
        try:
            removed = self.actor_manager.remove_actor(actor_type, actor_id)
            
            actor_key = f"{actor_type}:{actor_id}"
            
            return {
                'success': True,
                'removed': removed,
                'actorKey': actor_key
            }
            
        except Exception as e:
            return {
                'success': False,
                'removed': False,
                'error': {
                    'type': 'ActorRemovalError',
                    'message': str(e),
                    'details': {
                        'actor_type': actor_type,
                        'actor_id': actor_id
                    }
                }
            }

    def list_actors(
        self,
        actor_type: Optional[str] = None,
        include_hierarchy: bool = False
    ) -> Dict[str, Any]:
        """列出当前场景中的所有角色
        
        MCP Tool: list_actors
        
        Args:
            actor_type: 可选的角色类型过滤
            include_hierarchy: 是否包含层级关系信息
            
        Returns:
            角色列表，包含每个角色的详细信息
            
        Example:
            >>> tools.list_actors()
            {
                'actors': [
                    {
                        'actorType': 'server_id',
                        'actorId': 'server-01',
                        'description': '内存持续增长',
                        'parentActor': None,
                        'state': {},
                        'metadata': {...}
                    },
                    ...
                ],
                'count': 2
            }
        """
        try:
            actors = self.actor_manager.list_actors(actor_type=actor_type)
            
            actor_list = []
            for actor in actors:
                actor_info = {
                    'actorType': actor.actor_type,
                    'actorId': actor.actor_id,
                    'description': actor.description,
                    'parentActor': actor.parent_actor,
                    'state': actor.state,
                    'metadata': actor.metadata
                }
                
                # 如果需要包含层级信息
                if include_hierarchy and actor.parent_actor:
                    hierarchy = self.actor_manager.resolve_actor_hierarchy(
                        actor.actor_type,
                        actor.actor_id
                    )
                    actor_info['hierarchy'] = [
                        f"{a.actor_type}:{a.actor_id}" for a in hierarchy
                    ]
                
                actor_list.append(actor_info)
            
            return {
                'actors': actor_list,
                'count': len(actor_list)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'ActorListError',
                    'message': str(e),
                    'details': {
                        'actor_type': actor_type
                    }
                }
            }

    def get_actor_details(
        self,
        actor_type: str,
        actor_id: str,
        with_inheritance: bool = False
    ) -> Dict[str, Any]:
        """获取角色详细信息（辅助工具）
        
        Args:
            actor_type: 角色类型
            actor_id: 角色实例
            with_inheritance: 是否应用继承逻辑
            
        Returns:
            角色详细信息
        """
        try:
            if with_inheritance:
                actor = self.actor_manager.get_actor_with_inheritance(
                    actor_type, actor_id
                )
            else:
                actor = self.actor_manager.get_actor(actor_type, actor_id)
            
            if not actor:
                return {
                    'success': False,
                    'error': {
                        'type': 'ActorNotFoundError',
                        'message': f'Actor not found: {actor_type}:{actor_id}',
                        'details': {
                            'actor_type': actor_type,
                            'actor_id': actor_id
                        }
                    }
                }
            
            result = {
                'success': True,
                'actor': {
                    'actorType': actor.actor_type,
                    'actorId': actor.actor_id,
                    'description': actor.description,
                    'state': actor.state,
                    'parentActor': actor.parent_actor,
                    'metadata': actor.metadata
                }
            }
            
            # 如果应用了继承，添加层级信息
            if with_inheritance:
                hierarchy = self.actor_manager.resolve_actor_hierarchy(
                    actor_type, actor_id
                )
                result['hierarchy'] = [
                    f"{a.actor_type}:{a.actor_id}" for a in hierarchy
                ]
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'ActorDetailsError',
                    'message': str(e),
                    'details': {
                        'actor_type': actor_type,
                        'actor_id': actor_id
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
                'name': 'add_actor_config',
                'description': '为角色添加场景配置。支持追加场景描述而不覆盖已有配置。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'actor_type': {
                            'type': 'string',
                            'description': '角色类型（如 city, server_id, user_id）'
                        },
                        'actor_id': {
                            'type': 'string',
                            'description': '角色实例（如 深圳, server-01, user-001）'
                        },
                        'description': {
                            'type': 'string',
                            'description': '该角色的场景描述'
                        },
                        'parent_actor': {
                            'type': 'object',
                            'description': '可选的父级角色',
                            'properties': {
                                'actor_type': {'type': 'string'},
                                'actor_id': {'type': 'string'}
                            }
                        }
                    },
                    'required': ['actor_type', 'actor_id', 'description']
                }
            },
            {
                'name': 'remove_actor_config',
                'description': '删除特定角色的模拟配置，移除该角色的所有状态和行为数据。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'actor_type': {
                            'type': 'string',
                            'description': '角色类型'
                        },
                        'actor_id': {
                            'type': 'string',
                            'description': '角色实例'
                        }
                    },
                    'required': ['actor_type', 'actor_id']
                }
            },
            {
                'name': 'list_actors',
                'description': '查询当前场景中所有已配置的角色列表。',
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'actor_type': {
                            'type': 'string',
                            'description': '可选的角色类型过滤'
                        },
                        'include_hierarchy': {
                            'type': 'boolean',
                            'description': '是否包含层级关系信息',
                            'default': False
                        }
                    }
                }
            }
        ]
