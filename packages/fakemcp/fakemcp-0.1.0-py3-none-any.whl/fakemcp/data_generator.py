"""
Data Generator for FakeMCP

Generates mock data based on actor configurations, scenario descriptions,
plot graphs, and real example data.
"""

import json
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fakemcp.models import Actor, CausalityRelation, PlotNode, Scenario, TargetMCP
from fakemcp.plot_manager import PlotGraph


class DataGenerator:
    """数据生成器 - 根据角色配置和剧情图生成模拟数据"""

    def __init__(self):
        """Initialize data generator"""
        self.base_timestamp = datetime.now()

    def generate(
        self,
        target_mcp: TargetMCP,
        tool_name: str,
        parameters: dict,
        actors: List[Actor],
        scenario: Scenario,
        plot_graph: Optional[PlotGraph] = None
    ) -> Any:
        """生成模拟数据
        
        Args:
            target_mcp: 目标 MCP 服务器
            tool_name: 工具名称
            parameters: 调用参数
            actors: 涉及的角色列表
            scenario: 场景配置
            plot_graph: 可选的剧情图
            
        Returns:
            生成的模拟数据
        """
        # 从真实示例数据学习格式
        example_data = target_mcp.example_data.get(tool_name)
        
        # 识别参数中的角色
        involved_actors = self._identify_actors_in_parameters(
            parameters, target_mcp.actor_fields, actors
        )
        
        # 如果有剧情图，基于剧情生成
        if plot_graph:
            return self._generate_from_plot(
                plot_graph, tool_name, parameters, involved_actors, 
                scenario, example_data
            )
        
        # 否则基于角色配置生成
        return self._generate_from_actors(
            tool_name, parameters, involved_actors, 
            scenario, example_data
        )

    def generate_dataset_from_plot(
        self,
        plot_graph: PlotGraph,
        scenario: Scenario,
        target_mcps: Dict[str, TargetMCP],
        actors_map: Dict[str, Actor]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """基于剧情图生成完整数据集
        
        Args:
            plot_graph: 剧情图
            scenario: 场景配置
            target_mcps: 目标 MCP 映射 (id -> TargetMCP)
            actors_map: 角色映射 (actor_id -> Actor)
            
        Returns:
            按目标 MCP 分组的数据集
        """
        dataset = {}
        timeline = plot_graph.get_timeline()
        
        # 设置基准时间
        self.base_timestamp = datetime.now()
        
        # 按时间线生成数据
        for time_point in timeline:
            timestamp_offset = time_point['timestamp']
            events = time_point['events']
            
            for event_key in events:
                # 解析事件 (格式: "actor_id:event")
                parts = event_key.split(':', 1)
                if len(parts) != 2:
                    continue
                    
                actor_id, event = parts
                
                # 查找对应的剧情节点
                node = None
                for n in plot_graph.nodes.values():
                    if n.actor == actor_id and n.event == event:
                        node = n
                        break
                
                if not node:
                    continue
                
                # 获取角色
                actor = actors_map.get(actor_id)
                if not actor:
                    continue
                
                # 生成该节点的数据
                node_data = self._generate_data_for_node(
                    node, actor, scenario, target_mcps
                )
                
                # 按目标 MCP 分类
                for target_id, data_list in node_data.items():
                    if target_id not in dataset:
                        dataset[target_id] = []
                    dataset[target_id].extend(data_list)
        
        return dataset

    def learn_data_format(self, example_data: Any) -> Dict[str, Any]:
        """从真实示例数据学习数据格式
        
        Args:
            example_data: 真实返回数据示例
            
        Returns:
            数据格式模式
        """
        if not example_data:
            return {}
        
        pattern = {
            'type': type(example_data).__name__,
            'structure': {}
        }
        
        if isinstance(example_data, dict):
            pattern['structure'] = {
                key: self._analyze_field(value)
                for key, value in example_data.items()
            }
        elif isinstance(example_data, list) and example_data:
            pattern['is_list'] = True
            pattern['item_pattern'] = self.learn_data_format(example_data[0])
        
        return pattern

    def align_timestamps(
        self,
        data_list: List[Dict[str, Any]],
        base_timestamp: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """时间戳对齐算法
        
        Args:
            data_list: 数据列表
            base_timestamp: 基准时间戳
            
        Returns:
            对齐后的数据列表
        """
        if not base_timestamp:
            base_timestamp = self.base_timestamp
        
        aligned = []
        for data in data_list:
            aligned_data = self._align_single_timestamp(data, base_timestamp)
            aligned.append(aligned_data)
        
        return aligned

    def generate_causal_data(
        self,
        cause_actor: Actor,
        cause_event: str,
        effect_actor: Actor,
        effect_event: str,
        relation: CausalityRelation,
        scenario: Scenario,
        example_data: Optional[Any] = None
    ) -> Tuple[Any, Any]:
        """生成因果关系数据（确保原因在结果之前）
        
        Args:
            cause_actor: 原因角色
            cause_event: 原因事件
            effect_actor: 结果角色
            effect_event: 结果事件
            relation: 因果关系配置
            scenario: 场景配置
            example_data: 示例数据
            
        Returns:
            (原因数据, 结果数据) 元组
        """
        # 生成原因数据
        cause_timestamp = self.base_timestamp
        cause_data = self._generate_event_data(
            cause_actor, cause_event, cause_timestamp, scenario, example_data
        )
        
        # 生成结果数据（考虑时间延迟）
        effect_timestamp = cause_timestamp + timedelta(seconds=relation.time_delay)
        effect_data = self._generate_event_data(
            effect_actor, effect_event, effect_timestamp, scenario, example_data
        )
        
        # 根据因果强度调整结果数据的强度
        effect_data = self._adjust_effect_magnitude(
            effect_data, cause_data, relation.strength
        )
        
        return cause_data, effect_data

    def propagate_causality(
        self,
        source_actor: Actor,
        source_event: str,
        plot_graph: PlotGraph,
        timestamp: datetime,
        scenario: Scenario,
        actors_map: Dict[str, Actor]
    ) -> List[Tuple[str, str, datetime, Dict[str, Any]]]:
        """跨角色因果传播算法
        
        Args:
            source_actor: 源角色
            source_event: 源事件
            plot_graph: 剧情图
            timestamp: 源事件时间戳
            scenario: 场景配置
            actors_map: 角色映射
            
        Returns:
            受影响的事件列表 [(actor_id, event, timestamp, data), ...]
        """
        affected = []
        
        # 查找所有以 source_actor 为原因的因果关系
        outgoing_relations = plot_graph.get_outgoing_relations(source_actor.actor_id)
        
        for relation in outgoing_relations:
            # 只处理匹配的事件
            if relation.cause_event != source_event:
                continue
            
            effect_actor = actors_map.get(relation.effect_actor)
            if not effect_actor:
                continue
            
            # 计算结果时间
            effect_timestamp = timestamp + timedelta(seconds=relation.time_delay)
            
            # 生成结果数据
            effect_data = self._generate_event_data(
                effect_actor, relation.effect_event, effect_timestamp, scenario, None
            )
            
            affected.append((
                relation.effect_actor,
                relation.effect_event,
                effect_timestamp,
                effect_data
            ))
            
            # 递归传播
            propagated = self.propagate_causality(
                effect_actor,
                relation.effect_event,
                plot_graph,
                effect_timestamp,
                scenario,
                actors_map
            )
            affected.extend(propagated)
        
        return affected

    def _identify_actors_in_parameters(
        self,
        parameters: dict,
        actor_fields: List[str],
        actors: List[Actor]
    ) -> List[Actor]:
        """识别参数中涉及的角色
        
        Args:
            parameters: 调用参数
            actor_fields: 角色字段列表
            actors: 所有角色
            
        Returns:
            涉及的角色列表
        """
        involved = []
        
        for field in actor_fields:
            if field in parameters:
                actor_id = parameters[field]
                
                # 查找匹配的角色
                for actor in actors:
                    if actor.actor_id == actor_id:
                        involved.append(actor)
                        break
        
        return involved

    def _generate_from_plot(
        self,
        plot_graph: PlotGraph,
        tool_name: str,
        parameters: dict,
        actors: List[Actor],
        scenario: Scenario,
        example_data: Optional[Any]
    ) -> Any:
        """基于剧情图生成数据
        
        Args:
            plot_graph: 剧情图
            tool_name: 工具名称
            parameters: 调用参数
            actors: 涉及的角色
            scenario: 场景配置
            example_data: 示例数据
            
        Returns:
            生成的数据
        """
        if not actors:
            return self._generate_default_data(example_data)
        
        # 查找与角色相关的剧情节点
        relevant_nodes = []
        for actor in actors:
            for node in plot_graph.nodes.values():
                if node.actor == actor.actor_id:
                    relevant_nodes.append((actor, node))
        
        if not relevant_nodes:
            return self._generate_from_actors(
                tool_name, parameters, actors, scenario, example_data
            )
        
        # 基于剧情节点生成数据
        # 如果有多个节点，选择时间最近的
        relevant_nodes.sort(key=lambda x: x[1].timestamp_offset, reverse=True)
        actor, node = relevant_nodes[0]
        
        return self._generate_node_data(node, actor, scenario, example_data)

    def _generate_from_actors(
        self,
        tool_name: str,
        parameters: dict,
        actors: List[Actor],
        scenario: Scenario,
        example_data: Optional[Any]
    ) -> Any:
        """基于角色配置生成数据
        
        Args:
            tool_name: 工具名称
            parameters: 调用参数
            actors: 涉及的角色
            scenario: 场景配置
            example_data: 示例数据
            
        Returns:
            生成的数据
        """
        if not actors:
            return self._generate_default_data(example_data)
        
        # 使用第一个角色的配置
        actor = actors[0]
        
        # 学习数据格式
        data_pattern = self.learn_data_format(example_data)
        
        # 从角色描述中提取数据特征
        features = self._extract_features_from_description(actor.description)
        
        # 生成数据
        return self._generate_data_with_pattern(
            data_pattern, features, actor, scenario
        )

    def _generate_data_for_node(
        self,
        node: PlotNode,
        actor: Actor,
        scenario: Scenario,
        target_mcps: Dict[str, TargetMCP]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """为剧情节点生成数据
        
        Args:
            node: 剧情节点
            actor: 角色
            scenario: 场景配置
            target_mcps: 目标 MCP 映射
            
        Returns:
            按目标 MCP 分组的数据
        """
        result = {}
        
        # 计算时间戳
        timestamp = self.base_timestamp + timedelta(seconds=node.timestamp_offset)
        
        # 根据节点的 data_pattern 生成数据
        for target_id in scenario.target_mcps:
            target_mcp = target_mcps.get(target_id)
            if not target_mcp:
                continue
            
            # 生成该目标 MCP 的数据
            data = self._generate_node_data_for_target(
                node, actor, timestamp, target_mcp, scenario
            )
            
            if data:
                if target_id not in result:
                    result[target_id] = []
                result[target_id].append(data)
        
        return result

    def _generate_node_data(
        self,
        node: PlotNode,
        actor: Actor,
        scenario: Scenario,
        example_data: Optional[Any]
    ) -> Any:
        """生成剧情节点的数据
        
        Args:
            node: 剧情节点
            actor: 角色
            scenario: 场景配置
            example_data: 示例数据
            
        Returns:
            生成的数据
        """
        # 学习数据格式
        data_pattern = self.learn_data_format(example_data)
        
        # 合并节点的 data_pattern 和角色特征
        features = self._extract_features_from_description(actor.description)
        features.update(node.data_pattern)
        
        # 计算时间戳
        timestamp = self.base_timestamp + timedelta(seconds=node.timestamp_offset)
        features['timestamp'] = timestamp
        
        # 生成数据
        return self._generate_data_with_pattern(
            data_pattern, features, actor, scenario
        )

    def _generate_node_data_for_target(
        self,
        node: PlotNode,
        actor: Actor,
        timestamp: datetime,
        target_mcp: TargetMCP,
        scenario: Scenario
    ) -> Optional[Dict[str, Any]]:
        """为特定目标 MCP 生成节点数据
        
        Args:
            node: 剧情节点
            actor: 角色
            timestamp: 时间戳
            target_mcp: 目标 MCP
            scenario: 场景配置
            
        Returns:
            生成的数据，如果不适用则返回 None
        """
        # 从节点的 data_pattern 和角色描述提取特征
        features = self._extract_features_from_description(actor.description)
        features.update(node.data_pattern)
        features['timestamp'] = timestamp
        features['event'] = node.event
        
        # 根据目标 MCP 类型生成相应的数据
        # 这里简化处理，实际应该根据 Schema 生成
        data = {
            'actor_id': actor.actor_id,
            'actor_type': actor.actor_type,
            'timestamp': timestamp.isoformat(),
            'event': node.event,
            'data': features
        }
        
        return data

    def _generate_event_data(
        self,
        actor: Actor,
        event: str,
        timestamp: datetime,
        scenario: Scenario,
        example_data: Optional[Any]
    ) -> Dict[str, Any]:
        """生成事件数据
        
        Args:
            actor: 角色
            event: 事件描述
            timestamp: 时间戳
            scenario: 场景配置
            example_data: 示例数据
            
        Returns:
            生成的事件数据
        """
        # 从事件描述中提取特征
        features = self._extract_features_from_event(event)
        
        # 合并角色特征
        actor_features = self._extract_features_from_description(actor.description)
        features.update(actor_features)
        
        # 添加时间戳
        features['timestamp'] = timestamp
        
        # 学习数据格式
        data_pattern = self.learn_data_format(example_data)
        
        # 生成数据
        return self._generate_data_with_pattern(
            data_pattern, features, actor, scenario
        )

    def _generate_data_with_pattern(
        self,
        data_pattern: Dict[str, Any],
        features: Dict[str, Any],
        actor: Actor,
        scenario: Scenario
    ) -> Any:
        """根据数据模式和特征生成数据
        
        Args:
            data_pattern: 数据模式
            features: 提取的特征
            actor: 角色
            scenario: 场景配置
            
        Returns:
            生成的数据
        """
        if not data_pattern:
            # 没有模式，生成简单的数据
            return {
                'actor_id': actor.actor_id,
                'actor_type': actor.actor_type,
                'features': features,
                'scenario': scenario.description
            }
        
        if data_pattern.get('is_list'):
            # 生成列表数据
            item_pattern = data_pattern.get('item_pattern', {})
            # 生成 1-5 个项目
            count = random.randint(1, 5)
            return [
                self._generate_data_with_pattern(item_pattern, features, actor, scenario)
                for _ in range(count)
            ]
        
        if data_pattern.get('type') == 'dict':
            # 生成字典数据
            result = {}
            structure = data_pattern.get('structure', {})
            
            for key, field_info in structure.items():
                result[key] = self._generate_field_value(
                    key, field_info, features, actor
                )
            
            return result
        
        # 默认返回特征字典
        return features

    def _generate_field_value(
        self,
        field_name: str,
        field_info: Dict[str, Any],
        features: Dict[str, Any],
        actor: Actor
    ) -> Any:
        """生成字段值
        
        Args:
            field_name: 字段名
            field_info: 字段信息
            features: 特征字典
            actor: 角色
            
        Returns:
            生成的字段值
        """
        field_type = field_info.get('type', 'str')
        
        # 如果特征中有对应的值，使用它
        if field_name in features:
            return features[field_name]
        
        # 根据字段名和类型生成值
        if 'timestamp' in field_name.lower() or 'time' in field_name.lower():
            return features.get('timestamp', datetime.now()).isoformat()
        
        if field_name in ['actor_id', 'id', 'instance', 'server_id', 'user_id']:
            return actor.actor_id
        
        if field_name in ['actor_type', 'type']:
            return actor.actor_type
        
        if field_type == 'int' or field_type == 'float':
            # 从特征中提取数值
            return self._extract_numeric_value(features, field_name)
        
        if field_type == 'str':
            return f"{field_name}_value"
        
        if field_type == 'bool':
            return random.choice([True, False])
        
        return None

    def _extract_numeric_value(
        self,
        features: Dict[str, Any],
        field_name: str
    ) -> float:
        """从特征中提取数值
        
        Args:
            features: 特征字典
            field_name: 字段名
            
        Returns:
            提取的数值
        """
        # 查找相关的数值特征
        if 'memory' in field_name.lower():
            if 'memory' in features:
                return features['memory']
            if 'memory_trend' in features:
                trend = features['memory_trend']
                if trend == 'increasing':
                    return random.uniform(5.0, 10.0)  # GB
                elif trend == 'decreasing':
                    return random.uniform(0.5, 2.0)
                else:
                    return random.uniform(1.0, 4.0)
        
        if 'cpu' in field_name.lower():
            if 'cpu' in features:
                return features['cpu']
            return random.uniform(10.0, 90.0)  # percentage
        
        if 'error' in field_name.lower() or 'rate' in field_name.lower():
            if 'error_rate' in features:
                return features['error_rate']
            return random.uniform(0.0, 5.0)  # percentage
        
        # 默认返回随机值
        return random.uniform(0.0, 100.0)

    def _extract_features_from_description(
        self,
        description: str
    ) -> Dict[str, Any]:
        """从描述中提取特征
        
        Args:
            description: 描述文本
            
        Returns:
            提取的特征字典
        """
        features = {}
        
        # 提取数值和单位
        numeric_pattern = r'(\d+(?:\.\d+)?)\s*(GB|MB|KB|TB|ms|s|min|h|%|percent)'
        for match in re.finditer(numeric_pattern, description, re.IGNORECASE):
            value = float(match.group(1))
            unit = match.group(2).lower()
            
            if unit in ['gb', 'mb', 'kb', 'tb']:
                features['memory'] = value
                features['memory_unit'] = unit
            elif unit in ['ms', 's', 'min', 'h']:
                features['time'] = value
                features['time_unit'] = unit
            elif unit in ['%', 'percent']:
                features['percentage'] = value
        
        # 提取趋势关键词
        if any(kw in description.lower() for kw in ['增长', '上升', '增加', 'increasing', 'rising']):
            features['trend'] = 'increasing'
            features['memory_trend'] = 'increasing'
        elif any(kw in description.lower() for kw in ['下降', '减少', '降低', 'decreasing', 'falling']):
            features['trend'] = 'decreasing'
            features['memory_trend'] = 'decreasing'
        elif any(kw in description.lower() for kw in ['稳定', 'stable', '保持']):
            features['trend'] = 'stable'
        
        # 提取状态关键词
        if any(kw in description.lower() for kw in ['错误', 'error', '失败', 'failed', '故障']):
            features['status'] = 'error'
            features['error_rate'] = random.uniform(3.0, 10.0)
        elif any(kw in description.lower() for kw in ['警告', 'warning', '告警']):
            features['status'] = 'warning'
        elif any(kw in description.lower() for kw in ['正常', 'normal', '健康', 'healthy']):
            features['status'] = 'normal'
        
        # 提取内存泄露相关
        if any(kw in description.lower() for kw in ['内存泄露', 'memory leak', '内存增长']):
            features['memory_leak'] = True
            features['memory_trend'] = 'increasing'
        
        # 提取响应时间相关
        if any(kw in description.lower() for kw in ['响应慢', 'slow response', '延迟', 'latency']):
            features['response_slow'] = True
            features['response_time'] = random.uniform(1000, 5000)  # ms
        
        return features

    def _extract_features_from_event(self, event: str) -> Dict[str, Any]:
        """从事件描述中提取特征
        
        Args:
            event: 事件描述
            
        Returns:
            提取的特征字典
        """
        return self._extract_features_from_description(event)

    def _analyze_field(self, value: Any) -> Dict[str, Any]:
        """分析字段类型和特征
        
        Args:
            value: 字段值
            
        Returns:
            字段信息
        """
        field_info = {
            'type': type(value).__name__
        }
        
        if isinstance(value, (int, float)):
            field_info['numeric'] = True
            field_info['value_range'] = (value * 0.5, value * 1.5)
        elif isinstance(value, str):
            field_info['string'] = True
            field_info['length'] = len(value)
        elif isinstance(value, list):
            field_info['is_list'] = True
            if value:
                field_info['item_type'] = type(value[0]).__name__
        elif isinstance(value, dict):
            field_info['is_dict'] = True
            field_info['keys'] = list(value.keys())
        
        return field_info

    def _align_single_timestamp(
        self,
        data: Dict[str, Any],
        base_timestamp: datetime
    ) -> Dict[str, Any]:
        """对齐单个数据项的时间戳
        
        Args:
            data: 数据项
            base_timestamp: 基准时间戳
            
        Returns:
            对齐后的数据
        """
        aligned = data.copy()
        
        # 查找时间戳字段
        timestamp_fields = ['timestamp', 'time', 'created_at', 'updated_at', 'datetime']
        
        for field in timestamp_fields:
            if field in aligned:
                # 如果是字符串，解析它
                if isinstance(aligned[field], str):
                    try:
                        ts = datetime.fromisoformat(aligned[field].replace('Z', '+00:00'))
                        # 对齐到基准时间
                        aligned[field] = base_timestamp.isoformat()
                    except:
                        aligned[field] = base_timestamp.isoformat()
                elif isinstance(aligned[field], datetime):
                    aligned[field] = base_timestamp.isoformat()
        
        return aligned

    def _adjust_effect_magnitude(
        self,
        effect_data: Dict[str, Any],
        cause_data: Dict[str, Any],
        strength: float
    ) -> Dict[str, Any]:
        """根据因果强度调整结果数据的强度
        
        Args:
            effect_data: 结果数据
            cause_data: 原因数据
            strength: 因果强度 (0-1)
            
        Returns:
            调整后的结果数据
        """
        adjusted = effect_data.copy()
        
        # 查找数值字段并调整
        for key, value in adjusted.items():
            if isinstance(value, (int, float)):
                # 根据强度调整数值
                adjusted[key] = value * strength
        
        return adjusted

    def _generate_default_data(self, example_data: Optional[Any]) -> Any:
        """生成默认数据
        
        Args:
            example_data: 示例数据
            
        Returns:
            默认数据
        """
        if example_data:
            # 基于示例数据生成
            if isinstance(example_data, dict):
                return {k: self._generate_default_value(v) for k, v in example_data.items()}
            elif isinstance(example_data, list):
                return [self._generate_default_data(example_data[0])] if example_data else []
            else:
                return example_data
        
        # 返回空字典
        return {}

    def _generate_default_value(self, value: Any) -> Any:
        """生成默认值
        
        Args:
            value: 原始值
            
        Returns:
            生成的默认值
        """
        if isinstance(value, bool):
            return random.choice([True, False])
        elif isinstance(value, int):
            return random.randint(0, 100)
        elif isinstance(value, float):
            return random.uniform(0.0, 100.0)
        elif isinstance(value, str):
            return "default_value"
        elif isinstance(value, list):
            return []
        elif isinstance(value, dict):
            return {}
        else:
            return None
