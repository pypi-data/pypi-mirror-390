"""
Validation Service for FakeMCP

Validates mock data against schemas, checks logical consistency,
verifies causality relations, and validates plot graph consistency.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    import jsonschema
    from jsonschema import Draft7Validator, ValidationError
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from fakemcp.models import CausalityRelation, Scenario, TargetMCP
from fakemcp.plot_manager import PlotGraph, PlotManager


class ValidationService:
    """验证服务 - 验证数据、因果关系和剧情图的一致性"""

    def __init__(self, plot_manager: Optional[PlotManager] = None):
        """Initialize validation service
        
        Args:
            plot_manager: Optional PlotManager instance for plot validation
        """
        self.plot_manager = plot_manager

    def validate_schema(
        self,
        data: Any,
        schema: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """验证数据是否符合 JSON Schema
        
        Args:
            data: 要验证的数据
            schema: JSON Schema 定义
            
        Returns:
            (是否有效, 错误消息列表)
        """
        if not JSONSCHEMA_AVAILABLE:
            return True, ["jsonschema library not available, skipping schema validation"]
        
        if not schema:
            return True, []
        
        errors = []
        
        try:
            validator = Draft7Validator(schema)
            validation_errors = list(validator.iter_errors(data))
            
            for error in validation_errors:
                # 构建错误路径
                path = ".".join(str(p) for p in error.path) if error.path else "root"
                errors.append(f"Schema validation error at '{path}': {error.message}")
        
        except Exception as e:
            errors.append(f"Schema validation failed: {str(e)}")
        
        return len(errors) == 0, errors

    def validate_mock_data(
        self,
        mock_data: Any,
        target_mcp: TargetMCP,
        tool_name: str,
        scenario: Scenario
    ) -> Dict[str, Any]:
        """验证模拟数据的合理性
        
        Args:
            mock_data: 模拟数据
            target_mcp: 目标 MCP 服务器
            tool_name: 工具名称
            scenario: 场景配置
            
        Returns:
            验证结果字典
        """
        issues = []
        suggestions = []
        
        # 1. Schema 验证
        tool_schema = self._get_tool_output_schema(target_mcp, tool_name)
        if tool_schema:
            schema_valid, schema_errors = self.validate_schema(mock_data, tool_schema)
            if not schema_valid:
                issues.extend(schema_errors)
                suggestions.append(f"Adjust data structure to match {tool_name} output schema")
        
        # 2. 数据逻辑一致性检查
        consistency_issues = self._check_data_consistency(mock_data, scenario)
        issues.extend(consistency_issues)
        
        if consistency_issues:
            suggestions.append("Review data values to ensure they match scenario description")
        
        # 3. 时间戳验证
        timestamp_issues = self._validate_timestamps(mock_data)
        issues.extend(timestamp_issues)
        
        if timestamp_issues:
            suggestions.append("Ensure all timestamps are properly formatted and chronologically ordered")
        
        # 4. 数值范围检查
        range_issues = self._check_numeric_ranges(mock_data, scenario)
        issues.extend(range_issues)
        
        if range_issues:
            suggestions.append("Adjust numeric values to realistic ranges based on scenario context")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions
        }

    def validate_causality_relation(
        self,
        relation: CausalityRelation,
        actors_map: Dict[str, Any]
    ) -> Dict[str, Any]:
        """验证因果关系的有效性
        
        Args:
            relation: 因果关系
            actors_map: 角色映射 (actor_id -> Actor)
            
        Returns:
            验证结果字典
        """
        issues = []
        suggestions = []
        
        # 1. 检查角色是否存在
        if relation.cause_actor not in actors_map:
            issues.append(f"Cause actor '{relation.cause_actor}' not found in configured actors")
            suggestions.append(f"Add actor '{relation.cause_actor}' using add_actor_config")
        
        if relation.effect_actor not in actors_map:
            issues.append(f"Effect actor '{relation.effect_actor}' not found in configured actors")
            suggestions.append(f"Add actor '{relation.effect_actor}' using add_actor_config")
        
        # 2. 检查时间延迟
        if relation.time_delay < 0:
            issues.append(f"Time delay cannot be negative: {relation.time_delay}")
            suggestions.append("Set time_delay to a non-negative value (0 or greater)")
        
        # 3. 检查因果强度
        if not 0.0 <= relation.strength <= 1.0:
            issues.append(f"Causality strength must be between 0.0 and 1.0: {relation.strength}")
            suggestions.append("Set strength to a value between 0.0 and 1.0")
        
        # 4. 检查自引用（同一角色的因果关系是允许的，但需要不同的事件）
        if relation.cause_actor == relation.effect_actor and relation.cause_event == relation.effect_event:
            issues.append(f"Circular self-reference: actor '{relation.cause_actor}' with same event")
            suggestions.append("Ensure cause and effect events are different for the same actor")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions
        }

    def validate_plot_consistency(
        self,
        plot_graph: Optional[PlotGraph] = None
    ) -> Dict[str, Any]:
        """验证剧情图的一致性
        
        Args:
            plot_graph: 可选的剧情图，如果为 None 则使用 plot_manager 构建
            
        Returns:
            验证结果字典
        """
        if plot_graph is None and self.plot_manager:
            plot_graph = self.plot_manager.build_plot_graph()
        
        if plot_graph is None:
            return {
                'consistent': False,
                'issues': [{'type': 'error', 'description': 'No plot graph available for validation'}],
                'suggestions': ['Build a plot graph first using build_plot_graph']
            }
        
        # 使用 PlotManager 的验证功能
        if self.plot_manager:
            return self.plot_manager.validate_plot_consistency(plot_graph)
        
        # 如果没有 plot_manager，执行基本验证
        issues = []
        suggestions = []
        
        # 检查空图
        if not plot_graph.nodes:
            issues.append({
                'type': 'warning',
                'description': 'Plot graph has no nodes',
                'affectedNodes': []
            })
            suggestions.append('Add causality relations to build the plot graph')
        
        # 检查孤立节点
        isolated_nodes = self._find_isolated_nodes(plot_graph)
        if isolated_nodes:
            issues.append({
                'type': 'warning',
                'description': f'Found {len(isolated_nodes)} isolated nodes with no connections',
                'affectedNodes': isolated_nodes
            })
            suggestions.append('Connect isolated nodes with causality relations or remove them')
        
        return {
            'consistent': len([i for i in issues if i['type'] == 'error']) == 0,
            'issues': issues,
            'suggestions': suggestions
        }

    def check_data_consistency(
        self,
        data_set: List[Dict[str, Any]],
        scenario: Scenario,
        causality_relations: Optional[List[CausalityRelation]] = None
    ) -> Dict[str, Any]:
        """检查数据集的逻辑一致性
        
        Args:
            data_set: 数据集列表
            scenario: 场景配置
            causality_relations: 可选的因果关系列表
            
        Returns:
            一致性检查结果
        """
        issues = []
        suggestions = []
        
        # 1. 检查时间戳对齐
        timestamp_issues = self._check_timestamp_alignment(data_set)
        issues.extend(timestamp_issues)
        
        if timestamp_issues:
            suggestions.append("Use align_timestamps to synchronize timestamps across data sources")
        
        # 2. 检查因果关系一致性
        if causality_relations:
            causality_issues = self._check_causality_consistency(data_set, causality_relations)
            issues.extend(causality_issues)
            
            if causality_issues:
                suggestions.append("Ensure cause events occur before effect events with proper time delays")
        
        # 3. 检查数据语义一致性
        semantic_issues = self._check_semantic_consistency(data_set, scenario)
        issues.extend(semantic_issues)
        
        if semantic_issues:
            suggestions.append("Review data values to ensure they match the scenario description")
        
        # 4. 检查跨数据源一致性
        cross_source_issues = self._check_cross_source_consistency(data_set)
        issues.extend(cross_source_issues)
        
        if cross_source_issues:
            suggestions.append("Ensure related data across different sources tells a consistent story")
        
        return {
            'consistent': len(issues) == 0,
            'issues': issues,
            'suggestions': suggestions
        }

    def generate_correction_suggestions(
        self,
        validation_result: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """生成修正建议
        
        Args:
            validation_result: 验证结果
            context: 可选的上下文信息
            
        Returns:
            修正建议列表
        """
        suggestions = []
        
        # 从验证结果中提取建议
        if 'suggestions' in validation_result:
            suggestions.extend(validation_result['suggestions'])
        
        # 根据问题类型生成具体建议
        if 'issues' in validation_result:
            for issue in validation_result['issues']:
                if isinstance(issue, str):
                    # 字符串格式的问题
                    if 'schema' in issue.lower():
                        suggestions.append("Review the target MCP schema and adjust data structure accordingly")
                    elif 'timestamp' in issue.lower():
                        suggestions.append("Use ISO 8601 format for timestamps (YYYY-MM-DDTHH:MM:SS)")
                    elif 'range' in issue.lower() or 'value' in issue.lower():
                        suggestions.append("Adjust numeric values to realistic ranges")
                elif isinstance(issue, dict):
                    # 字典格式的问题
                    issue_type = issue.get('type', '')
                    
                    if issue_type == 'circular_dependency':
                        suggestions.append("Remove one or more causality relations to break the cycle")
                    elif issue_type == 'time_conflict':
                        suggestions.append("Increase time_delay values to ensure proper event ordering")
                    elif issue_type == 'missing_actor':
                        suggestions.append("Add missing actors before building the plot graph")
        
        # 去重
        suggestions = list(dict.fromkeys(suggestions))
        
        return suggestions

    def _get_tool_output_schema(
        self,
        target_mcp: TargetMCP,
        tool_name: str
    ) -> Optional[Dict[str, Any]]:
        """获取工具的输出 Schema
        
        Args:
            target_mcp: 目标 MCP
            tool_name: 工具名称
            
        Returns:
            输出 Schema，如果未找到则返回 None
        """
        if not target_mcp.schema or 'tools' not in target_mcp.schema:
            return None
        
        for tool in target_mcp.schema['tools']:
            if tool.get('name') == tool_name:
                return tool.get('outputSchema')
        
        return None

    def _check_data_consistency(
        self,
        data: Any,
        scenario: Scenario
    ) -> List[str]:
        """检查数据的逻辑一致性
        
        Args:
            data: 数据
            scenario: 场景配置
            
        Returns:
            问题列表
        """
        issues = []
        
        # 检查数据是否为空
        if data is None:
            issues.append("Data is None")
            return issues
        
        # 检查数据结构
        if isinstance(data, dict):
            # 检查是否有基本字段
            if not data:
                issues.append("Data dictionary is empty")
        elif isinstance(data, list):
            if not data:
                issues.append("Data list is empty")
        
        return issues

    def _validate_timestamps(self, data: Any) -> List[str]:
        """验证时间戳格式
        
        Args:
            data: 数据
            
        Returns:
            问题列表
        """
        issues = []
        
        def check_timestamp_field(obj: Any, path: str = ""):
            """递归检查时间戳字段"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # 检查时间戳字段
                    if any(ts_key in key.lower() for ts_key in ['timestamp', 'time', 'date', 'created', 'updated']):
                        if isinstance(value, str):
                            # 尝试解析时间戳
                            try:
                                datetime.fromisoformat(value.replace('Z', '+00:00'))
                            except (ValueError, AttributeError):
                                issues.append(f"Invalid timestamp format at '{current_path}': {value}")
                        elif not isinstance(value, (int, float, datetime)):
                            issues.append(f"Unexpected timestamp type at '{current_path}': {type(value).__name__}")
                    else:
                        check_timestamp_field(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_timestamp_field(item, f"{path}[{i}]")
        
        check_timestamp_field(data)
        return issues

    def _check_numeric_ranges(
        self,
        data: Any,
        scenario: Scenario
    ) -> List[str]:
        """检查数值范围的合理性
        
        Args:
            data: 数据
            scenario: 场景配置
            
        Returns:
            问题列表
        """
        issues = []
        
        def check_numeric_field(obj: Any, path: str = ""):
            """递归检查数值字段"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    if isinstance(value, (int, float)):
                        # 检查常见指标的范围
                        if 'percent' in key.lower() or 'rate' in key.lower():
                            if not 0 <= value <= 100:
                                issues.append(f"Percentage value out of range at '{current_path}': {value}")
                        elif 'memory' in key.lower() and 'gb' in key.lower():
                            if value < 0 or value > 1024:  # 假设最大 1TB
                                issues.append(f"Memory value seems unrealistic at '{current_path}': {value} GB")
                        elif 'cpu' in key.lower():
                            if not 0 <= value <= 100:
                                issues.append(f"CPU value out of range at '{current_path}': {value}")
                    else:
                        check_numeric_field(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_numeric_field(item, f"{path}[{i}]")
        
        check_numeric_field(data)
        return issues

    def _check_timestamp_alignment(
        self,
        data_set: List[Dict[str, Any]]
    ) -> List[str]:
        """检查时间戳对齐
        
        Args:
            data_set: 数据集
            
        Returns:
            问题列表
        """
        issues = []
        
        if len(data_set) < 2:
            return issues
        
        # 提取所有时间戳
        timestamps = []
        for i, data in enumerate(data_set):
            ts = self._extract_timestamp(data)
            if ts:
                timestamps.append((i, ts))
        
        if len(timestamps) < 2:
            return issues
        
        # 检查时间戳是否合理分布
        timestamps.sort(key=lambda x: x[1])
        
        # 检查是否有时间戳相同但应该不同的情况
        for i in range(len(timestamps) - 1):
            if timestamps[i][1] == timestamps[i + 1][1]:
                issues.append(
                    f"Data items {timestamps[i][0]} and {timestamps[i + 1][0]} have identical timestamps"
                )
        
        return issues

    def _check_causality_consistency(
        self,
        data_set: List[Dict[str, Any]],
        causality_relations: List[CausalityRelation]
    ) -> List[str]:
        """检查因果关系一致性
        
        Args:
            data_set: 数据集
            causality_relations: 因果关系列表
            
        Returns:
            问题列表
        """
        issues = []
        
        # 为每个因果关系检查数据
        for relation in causality_relations:
            cause_data = None
            effect_data = None
            
            # 查找原因和结果数据
            for data in data_set:
                actor_id = data.get('actor_id') or data.get('id')
                event = data.get('event')
                
                if actor_id == relation.cause_actor and event == relation.cause_event:
                    cause_data = data
                elif actor_id == relation.effect_actor and event == relation.effect_event:
                    effect_data = data
            
            # 检查是否找到数据
            if not cause_data:
                issues.append(
                    f"No data found for cause: {relation.cause_actor}:{relation.cause_event}"
                )
                continue
            
            if not effect_data:
                issues.append(
                    f"No data found for effect: {relation.effect_actor}:{relation.effect_event}"
                )
                continue
            
            # 检查时间顺序
            cause_ts = self._extract_timestamp(cause_data)
            effect_ts = self._extract_timestamp(effect_data)
            
            if cause_ts and effect_ts:
                time_diff = (effect_ts - cause_ts).total_seconds()
                
                if time_diff < 0:
                    issues.append(
                        f"Effect occurs before cause: {relation.effect_actor}:{relation.effect_event} "
                        f"before {relation.cause_actor}:{relation.cause_event}"
                    )
                elif time_diff < relation.time_delay:
                    issues.append(
                        f"Time delay too short: expected {relation.time_delay}s, "
                        f"got {time_diff}s for {relation.cause_actor} -> {relation.effect_actor}"
                    )
        
        return issues

    def _check_semantic_consistency(
        self,
        data_set: List[Dict[str, Any]],
        scenario: Scenario
    ) -> List[str]:
        """检查语义一致性
        
        Args:
            data_set: 数据集
            scenario: 场景配置
            
        Returns:
            问题列表
        """
        issues = []
        
        # 从场景描述中提取关键词
        scenario_keywords = self._extract_keywords(scenario.description)
        
        # 检查数据是否反映场景关键词
        # 这是一个简化的实现，实际可能需要更复杂的语义分析
        
        return issues

    def _check_cross_source_consistency(
        self,
        data_set: List[Dict[str, Any]]
    ) -> List[str]:
        """检查跨数据源一致性
        
        Args:
            data_set: 数据集
            
        Returns:
            问题列表
        """
        issues = []
        
        # 按角色分组数据
        actor_data_map: Dict[str, List[Dict[str, Any]]] = {}
        
        for data in data_set:
            actor_id = data.get('actor_id') or data.get('id')
            if actor_id:
                if actor_id not in actor_data_map:
                    actor_data_map[actor_id] = []
                actor_data_map[actor_id].append(data)
        
        # 检查同一角色的数据是否一致
        for actor_id, actor_data_list in actor_data_map.items():
            if len(actor_data_list) > 1:
                # 检查状态是否一致
                statuses = [d.get('status') for d in actor_data_list if 'status' in d]
                if len(set(statuses)) > 1:
                    issues.append(
                        f"Inconsistent status values for actor '{actor_id}': {statuses}"
                    )
        
        return issues

    def _find_isolated_nodes(self, plot_graph: PlotGraph) -> List[str]:
        """查找孤立节点
        
        Args:
            plot_graph: 剧情图
            
        Returns:
            孤立节点 ID 列表
        """
        isolated = []
        
        for node_id, node in plot_graph.nodes.items():
            # 检查是否有入边或出边
            has_incoming = any(
                edge.effect_actor == node.actor and edge.effect_event == node.event
                for edge in plot_graph.edges
            )
            has_outgoing = any(
                edge.cause_actor == node.actor and edge.cause_event == node.event
                for edge in plot_graph.edges
            )
            
            if not has_incoming and not has_outgoing:
                isolated.append(node_id)
        
        return isolated

    def _extract_timestamp(self, data: Dict[str, Any]) -> Optional[datetime]:
        """从数据中提取时间戳
        
        Args:
            data: 数据字典
            
        Returns:
            时间戳，如果未找到则返回 None
        """
        timestamp_fields = ['timestamp', 'time', 'created_at', 'updated_at', 'datetime']
        
        for field in timestamp_fields:
            if field in data:
                value = data[field]
                
                if isinstance(value, datetime):
                    return value
                elif isinstance(value, str):
                    try:
                        return datetime.fromisoformat(value.replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        continue
                elif isinstance(value, (int, float)):
                    try:
                        return datetime.fromtimestamp(value)
                    except (ValueError, OSError):
                        continue
        
        return None

    def _extract_keywords(self, text: str) -> List[str]:
        """从文本中提取关键词
        
        Args:
            text: 文本
            
        Returns:
            关键词列表
        """
        # 简化实现：分词并过滤常见词
        import re
        
        # 分词
        words = re.findall(r'\w+', text.lower())
        
        # 过滤停用词（简化版）
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        return keywords
