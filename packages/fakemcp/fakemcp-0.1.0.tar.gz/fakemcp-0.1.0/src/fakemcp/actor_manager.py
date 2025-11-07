"""
Actor Manager for FakeMCP

Manages actor lifecycle including creation, deletion, querying,
hierarchical relationships, inheritance logic, and actor extraction
from scenario descriptions.
"""

import re
from typing import Dict, List, Optional, Set

from fakemcp.database import Database
from fakemcp.models import Actor


class ActorManager:
    """角色管理器 - 管理场景中的角色实体"""

    def __init__(self, database: Database):
        """Initialize actor manager
        
        Args:
            database: Database instance for persistence
        """
        self.db = database

    def add_actor(
        self,
        actor_type: str,
        actor_id: str,
        description: str,
        state: Optional[Dict] = None,
        parent_actor: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict] = None
    ) -> Actor:
        """添加角色
        
        Args:
            actor_type: 角色类型（如 'city', 'server_id', 'user_id'）
            actor_id: 角色实例（如 '深圳', 'server-01', 'user-001'）
            description: 角色的场景描述
            state: 角色状态（可选）
            parent_actor: 父级角色（可选），格式: {'actor_type': 'city', 'actor_id': '深圳'}
            metadata: 元数据（可选）
            
        Returns:
            创建的 Actor 对象
        """
        if state is None:
            state = {}
        if metadata is None:
            metadata = {}
        
        # 从描述中提取属性
        extracted_metadata = self._extract_metadata_from_description(description)
        metadata.update(extracted_metadata)
        
        actor = Actor(
            actor_type=actor_type,
            actor_id=actor_id,
            description=description,
            state=state,
            parent_actor=parent_actor,
            metadata=metadata
        )
        
        # 检查是否已存在
        existing = self.db.get_actor(actor_type, actor_id)
        if existing:
            # 更新现有角色
            self.db.update_actor(actor)
        else:
            # 创建新角色
            self.db.create_actor(actor)
        
        return actor

    def remove_actor(self, actor_type: str, actor_id: str) -> bool:
        """删除角色
        
        Args:
            actor_type: 角色类型
            actor_id: 角色实例
            
        Returns:
            是否成功删除
        """
        actor = self.db.get_actor(actor_type, actor_id)
        if not actor:
            return False
        
        self.db.delete_actor(actor_type, actor_id)
        return True

    def get_actor(self, actor_type: str, actor_id: str) -> Optional[Actor]:
        """获取角色
        
        Args:
            actor_type: 角色类型
            actor_id: 角色实例
            
        Returns:
            Actor 对象，如果不存在则返回 None
        """
        return self.db.get_actor(actor_type, actor_id)

    def list_actors(
        self,
        actor_type: Optional[str] = None
    ) -> List[Actor]:
        """列出所有角色
        
        Args:
            actor_type: 可选的角色类型过滤
            
        Returns:
            角色列表
        """
        actors = self.db.list_actors()
        
        if actor_type:
            actors = [a for a in actors if a.actor_type == actor_type]
        
        return actors

    def resolve_actor_hierarchy(
        self,
        actor_type: str,
        actor_id: str
    ) -> List[Actor]:
        """解析角色层级关系
        
        从当前角色向上遍历到根角色，返回完整的继承链。
        返回列表从根角色到当前角色排序。
        
        Args:
            actor_type: 角色类型
            actor_id: 角色实例
            
        Returns:
            角色继承链列表，从根到叶子排序
            
        Example:
            深圳南山区 -> [深圳, 深圳南山区]
        """
        hierarchy = []
        current_actor = self.db.get_actor(actor_type, actor_id)
        
        if not current_actor:
            return hierarchy
        
        # 向上遍历父级
        visited = set()  # 防止循环引用
        while current_actor:
            # 检查循环引用
            actor_key = f"{current_actor.actor_type}:{current_actor.actor_id}"
            if actor_key in visited:
                break
            visited.add(actor_key)
            
            hierarchy.append(current_actor)
            
            # 获取父级
            if current_actor.parent_actor:
                parent_type = current_actor.parent_actor.get('actor_type')
                parent_id = current_actor.parent_actor.get('actor_id')
                if parent_type and parent_id:
                    current_actor = self.db.get_actor(parent_type, parent_id)
                else:
                    break
            else:
                break
        
        # 反转列表，使其从根到叶子排序
        hierarchy.reverse()
        return hierarchy

    def get_actor_with_inheritance(
        self,
        actor_type: str,
        actor_id: str
    ) -> Optional[Actor]:
        """获取角色并应用继承逻辑
        
        子角色继承父角色的配置，子角色的配置会覆盖父角色的配置。
        
        Args:
            actor_type: 角色类型
            actor_id: 角色实例
            
        Returns:
            合并后的 Actor 对象，如果不存在则返回 None
        """
        hierarchy = self.resolve_actor_hierarchy(actor_type, actor_id)
        
        if not hierarchy:
            return None
        
        # 从根到叶子合并配置
        merged_state = {}
        merged_metadata = {}
        merged_description_parts = []
        
        for actor in hierarchy:
            # 合并 state
            merged_state.update(actor.state)
            
            # 合并 metadata
            merged_metadata.update(actor.metadata)
            
            # 收集描述
            if actor.description:
                merged_description_parts.append(actor.description)
        
        # 使用最后一个（叶子）角色作为基础
        leaf_actor = hierarchy[-1]
        
        # 创建合并后的角色对象
        merged_actor = Actor(
            actor_type=leaf_actor.actor_type,
            actor_id=leaf_actor.actor_id,
            description=' | '.join(merged_description_parts),
            state=merged_state,
            parent_actor=leaf_actor.parent_actor,
            metadata=merged_metadata
        )
        
        return merged_actor

    def extract_actors_from_description(
        self,
        description: str,
        actor_fields: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """从场景描述中提取角色实例
        
        使用模式匹配识别可能的角色实例。
        
        Args:
            description: 场景描述
            actor_fields: 可选的角色字段提示列表（如 ['city', 'server_id']）
            
        Returns:
            提取的角色列表，格式: [{'actor_type': 'city', 'actor_id': '深圳'}, ...]
        """
        actors = []
        
        # 模式 1: 识别服务器 ID（server-01, server_01, srv-001）
        server_pattern = r'\b(server|srv|host|node)[-_]?(\w+)\b'
        for match in re.finditer(server_pattern, description, re.IGNORECASE):
            actor_id = match.group(0)
            actors.append({
                'actor_type': 'server_id',
                'actor_id': actor_id
            })
        
        # 模式 2: 识别用户 ID（user-001, user_123, uid-456）
        user_pattern = r'\b(user|uid)[-_]?(\w+)\b'
        for match in re.finditer(user_pattern, description, re.IGNORECASE):
            actor_id = match.group(0)
            actors.append({
                'actor_type': 'user_id',
                'actor_id': actor_id
            })
        
        # 模式 3: 识别中文城市名（深圳、北京、上海等）
        chinese_city_pattern = r'(北京|上海|广州|深圳|杭州|成都|重庆|武汉|西安|南京|天津|苏州|长沙|郑州|东莞|青岛|沈阳|宁波|昆明|大连|厦门|合肥|佛山|福州|哈尔滨|济南|温州|长春|石家庄|常州|泉州|南宁|贵阳|南昌|南通|金华|徐州|太原|嘉兴|烟台|惠州|保定|台州|中山|绍兴|乌鲁木齐|潍坊|兰州)'
        for match in re.finditer(chinese_city_pattern, description):
            city_name = match.group(0)
            actors.append({
                'actor_type': 'city',
                'actor_id': city_name
            })
        
        # 模式 4: 识别城市区域（深圳南山区、北京朝阳区）
        district_pattern = r'([\u4e00-\u9fff]{2,})([\u4e00-\u9fff]{2,}区)'
        for match in re.finditer(district_pattern, description):
            city = match.group(1)
            district = match.group(0)
            actors.append({
                'actor_type': 'district',
                'actor_id': district,
                'parent_city': city
            })
        
        # 模式 5: 识别数据库实例（database-01, db-prod, mysql-001）
        db_pattern = r'\b(database|db|mysql|postgres|mongodb|redis)[-_]?(\w+)\b'
        for match in re.finditer(db_pattern, description, re.IGNORECASE):
            actor_id = match.group(0)
            actors.append({
                'actor_type': 'database_id',
                'actor_id': actor_id
            })
        
        # 模式 6: 识别应用/服务名称（app-name, service-name）
        app_pattern = r'\b(app|application|service|svc)[-_]?(\w+)\b'
        for match in re.finditer(app_pattern, description, re.IGNORECASE):
            actor_id = match.group(0)
            actors.append({
                'actor_type': 'application_id',
                'actor_id': actor_id
            })
        
        # 去重（保持顺序）
        seen = set()
        unique_actors = []
        for actor in actors:
            key = f"{actor['actor_type']}:{actor['actor_id']}"
            if key not in seen:
                seen.add(key)
                unique_actors.append(actor)
        
        return unique_actors

    def create_actors_from_extraction(
        self,
        extracted_actors: List[Dict[str, str]],
        default_description: str = ""
    ) -> List[Actor]:
        """从提取的角色信息创建角色对象
        
        Args:
            extracted_actors: 提取的角色列表
            default_description: 默认描述（如果提取信息中没有描述）
            
        Returns:
            创建的 Actor 对象列表
        """
        created_actors = []
        
        for actor_info in extracted_actors:
            actor_type = actor_info['actor_type']
            actor_id = actor_info['actor_id']
            
            # 处理父级关系
            parent_actor = None
            if 'parent_city' in actor_info:
                parent_actor = {
                    'actor_type': 'city',
                    'actor_id': actor_info['parent_city']
                }
            
            description = actor_info.get('description', default_description)
            
            actor = self.add_actor(
                actor_type=actor_type,
                actor_id=actor_id,
                description=description,
                parent_actor=parent_actor
            )
            
            created_actors.append(actor)
        
        return created_actors

    def _extract_metadata_from_description(self, description: str) -> Dict:
        """从描述中提取元数据
        
        识别描述中的关键信息并提取为结构化元数据。
        
        Args:
            description: 角色描述
            
        Returns:
            提取的元数据字典
        """
        metadata = {}
        
        # 提取数值和单位（如 "2GB", "100ms", "50%"）
        numeric_pattern = r'(\d+(?:\.\d+)?)\s*(GB|MB|KB|TB|ms|s|min|h|%|percent)'
        for match in re.finditer(numeric_pattern, description, re.IGNORECASE):
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            # 根据单位分类
            if unit in ['gb', 'mb', 'kb', 'tb']:
                if 'memory' not in metadata:
                    metadata['memory'] = []
                metadata['memory'].append({'value': value, 'unit': unit})
            elif unit in ['ms', 's', 'min', 'h']:
                if 'time' not in metadata:
                    metadata['time'] = []
                metadata['time'].append({'value': value, 'unit': unit})
            elif unit in ['%', 'percent']:
                if 'percentage' not in metadata:
                    metadata['percentage'] = []
                metadata['percentage'].append({'value': value, 'unit': '%'})
        
        # 提取状态关键词
        status_keywords = {
            'normal': ['正常', 'normal', 'healthy', '健康'],
            'warning': ['警告', 'warning', '告警', 'alert'],
            'error': ['错误', 'error', '失败', 'failed', '故障', 'fault'],
            'critical': ['严重', 'critical', '危急', '紧急', 'emergency'],
            'good': ['好', 'good', '良好', 'excellent', '优秀'],
            'bad': ['差', 'bad', '糟糕', 'poor', '恶劣']
        }
        
        for status, keywords in status_keywords.items():
            for keyword in keywords:
                if keyword in description.lower():
                    metadata['status'] = status
                    break
            if 'status' in metadata:
                break
        
        # 提取趋势关键词
        trend_keywords = {
            'increasing': ['增长', '上升', '增加', 'increasing', 'rising', 'growing', '升高'],
            'decreasing': ['下降', '减少', '降低', 'decreasing', 'falling', 'dropping'],
            'stable': ['稳定', 'stable', '保持', 'constant', '不变'],
            'fluctuating': ['波动', '变化', 'fluctuating', 'varying', '不稳定']
        }
        
        for trend, keywords in trend_keywords.items():
            for keyword in keywords:
                if keyword in description.lower():
                    metadata['trend'] = trend
                    break
            if 'trend' in metadata:
                break
        
        return metadata

    def update_actor_state(
        self,
        actor_type: str,
        actor_id: str,
        state_updates: Dict
    ) -> Optional[Actor]:
        """更新角色状态
        
        Args:
            actor_type: 角色类型
            actor_id: 角色实例
            state_updates: 状态更新字典
            
        Returns:
            更新后的 Actor 对象，如果不存在则返回 None
        """
        actor = self.db.get_actor(actor_type, actor_id)
        if not actor:
            return None
        
        actor.state.update(state_updates)
        self.db.update_actor(actor)
        
        return actor

    def find_child_actors(
        self,
        parent_type: str,
        parent_id: str
    ) -> List[Actor]:
        """查找指定父级的所有子角色
        
        Args:
            parent_type: 父级角色类型
            parent_id: 父级角色实例
            
        Returns:
            子角色列表
        """
        all_actors = self.db.list_actors()
        children = []
        
        for actor in all_actors:
            if actor.parent_actor:
                if (actor.parent_actor.get('actor_type') == parent_type and
                    actor.parent_actor.get('actor_id') == parent_id):
                    children.append(actor)
        
        return children
