"""
Scenario Manager for FakeMCP

Manages scenario lifecycle including creation, updates, deletion,
keyword extraction, and file persistence (YAML format).
"""

import re
import uuid
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from fakemcp.database import Database
from fakemcp.models import Scenario


class ScenarioManager:
    """场景管理器 - 管理测试场景的完整生命周期"""

    def __init__(self, database: Database):
        """Initialize scenario manager
        
        Args:
            database: Database instance for persistence
        """
        self.db = database

    def create_scenario(
        self,
        description: str,
        target_mcps: Optional[List[str]] = None
    ) -> Scenario:
        """创建新场景
        
        Args:
            description: 场景描述（自然语言）
            target_mcps: 目标 MCP 服务器 ID 列表
            
        Returns:
            创建的 Scenario 对象
        """
        if target_mcps is None:
            target_mcps = []
            
        scenario_id = self._generate_scenario_id()
        now = datetime.now()
        
        # 提取关键词
        keywords = self._extract_keywords(description)
        
        scenario = Scenario(
            id=scenario_id,
            description=description,
            target_mcps=target_mcps,
            created_at=now,
            updated_at=now,
            metadata={
                'keywords': keywords,
                'extracted_actors': [],
                'causality_relations': [],
                'plot_graph': None
            }
        )
        
        self.db.create_scenario(scenario)
        return scenario

    def get_scenario(self, scenario_id: str) -> Optional[Scenario]:
        """获取场景
        
        Args:
            scenario_id: 场景 ID
            
        Returns:
            Scenario 对象，如果不存在则返回 None
        """
        return self.db.get_scenario(scenario_id)

    def update_scenario(
        self,
        scenario_id: str,
        description: Optional[str] = None,
        target_mcps: Optional[List[str]] = None,
        metadata_updates: Optional[Dict[str, Any]] = None
    ) -> Optional[Scenario]:
        """更新场景
        
        Args:
            scenario_id: 场景 ID
            description: 新的场景描述（可选）
            target_mcps: 新的目标 MCP 列表（可选）
            metadata_updates: 元数据更新（可选）
            
        Returns:
            更新后的 Scenario 对象，如果场景不存在则返回 None
        """
        scenario = self.db.get_scenario(scenario_id)
        if not scenario:
            return None
        
        # 更新字段
        if description is not None:
            scenario.description = description
            # 重新提取关键词
            keywords = self._extract_keywords(description)
            scenario.metadata['keywords'] = keywords
            
        if target_mcps is not None:
            scenario.target_mcps = target_mcps
            
        if metadata_updates:
            scenario.metadata.update(metadata_updates)
        
        scenario.updated_at = datetime.now()
        self.db.update_scenario(scenario)
        
        return scenario

    def delete_scenario(self, scenario_id: str) -> bool:
        """删除场景
        
        Args:
            scenario_id: 场景 ID
            
        Returns:
            是否成功删除
        """
        scenario = self.db.get_scenario(scenario_id)
        if not scenario:
            return False
            
        self.db.delete_scenario(scenario_id)
        return True

    def list_scenarios(self) -> List[Scenario]:
        """列出所有场景
        
        Returns:
            所有场景的列表
        """
        return self.db.list_scenarios()

    def save_to_file(self, scenario_id: str, filepath: str) -> bool:
        """保存场景到 YAML 文件
        
        Args:
            scenario_id: 场景 ID
            filepath: 文件路径
            
        Returns:
            是否成功保存
        """
        scenario = self.db.get_scenario(scenario_id)
        if not scenario:
            return False
        
        # 获取相关的 actors
        actors = self.db.list_actors()
        
        # 获取相关的 target MCPs
        target_mcps = []
        for target_id in scenario.target_mcps:
            target_mcp = self.db.get_target_mcp(target_id)
            if target_mcp:
                target_mcps.append({
                    'id': target_mcp.id,
                    'name': target_mcp.name,
                    'url': target_mcp.url,
                    'config': target_mcp.config,
                    'actor_fields': target_mcp.actor_fields
                })
        
        # 获取因果关系
        causality_relations = self.db.list_causality_relations()
        
        # 构建 YAML 数据结构
        data = {
            'scenario': {
                'id': scenario.id,
                'description': scenario.description,
                'created_at': scenario.created_at.isoformat(),
                'updated_at': scenario.updated_at.isoformat(),
                'metadata': scenario.metadata
            },
            'target_mcps': target_mcps,
            'actors': [
                {
                    'actor_type': actor.actor_type,
                    'actor_id': actor.actor_id,
                    'description': actor.description,
                    'state': actor.state,
                    'parent_actor': actor.parent_actor,
                    'metadata': actor.metadata
                }
                for actor in actors
            ],
            'causality_relations': [
                {
                    'cause_actor': rel.cause_actor,
                    'cause_event': rel.cause_event,
                    'effect_actor': rel.effect_actor,
                    'effect_event': rel.effect_event,
                    'time_delay': rel.time_delay,
                    'strength': rel.strength
                }
                for rel in causality_relations
            ]
        }
        
        # 确保目录存在
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # 写入 YAML 文件
        with open(filepath, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        
        return True

    def load_from_file(self, filepath: str) -> Optional[Scenario]:
        """从 YAML 文件加载场景
        
        Args:
            filepath: 文件路径
            
        Returns:
            加载的 Scenario 对象，如果失败则返回 None
        """
        if not Path(filepath).exists():
            return None
        
        # 读取 YAML 文件
        with open(filepath, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'scenario' not in data:
            return None
        
        scenario_data = data['scenario']
        
        # 创建场景
        scenario = Scenario(
            id=scenario_data['id'],
            description=scenario_data['description'],
            target_mcps=[mcp['id'] for mcp in data.get('target_mcps', [])],
            created_at=datetime.fromisoformat(scenario_data['created_at']),
            updated_at=datetime.fromisoformat(scenario_data['updated_at']),
            metadata=scenario_data.get('metadata', {})
        )
        
        # 保存到数据库（如果已存在则更新）
        existing = self.db.get_scenario(scenario.id)
        if existing:
            self.db.update_scenario(scenario)
        else:
            self.db.create_scenario(scenario)
        
        # 加载 target MCPs
        from fakemcp.models import TargetMCP
        for mcp_data in data.get('target_mcps', []):
            target_mcp = TargetMCP(
                id=mcp_data['id'],
                name=mcp_data['name'],
                url=mcp_data['url'],
                config=mcp_data.get('config', {}),
                schema={},  # Schema 需要重新获取
                actor_fields=mcp_data.get('actor_fields', []),
                example_data={},
                connected=False
            )
            
            existing_mcp = self.db.get_target_mcp(target_mcp.id)
            if existing_mcp:
                self.db.update_target_mcp(target_mcp)
            else:
                self.db.create_target_mcp(target_mcp)
        
        # 加载 actors
        from fakemcp.models import Actor
        for actor_data in data.get('actors', []):
            actor = Actor(
                actor_type=actor_data['actor_type'],
                actor_id=actor_data['actor_id'],
                description=actor_data['description'],
                state=actor_data.get('state', {}),
                parent_actor=actor_data.get('parent_actor'),
                metadata=actor_data.get('metadata', {})
            )
            
            existing_actor = self.db.get_actor(actor.actor_type, actor.actor_id)
            if existing_actor:
                self.db.update_actor(actor)
            else:
                self.db.create_actor(actor)
        
        # 加载因果关系
        from fakemcp.models import CausalityRelation
        for rel_data in data.get('causality_relations', []):
            relation = CausalityRelation(
                cause_actor=rel_data['cause_actor'],
                cause_event=rel_data['cause_event'],
                effect_actor=rel_data['effect_actor'],
                effect_event=rel_data['effect_event'],
                time_delay=rel_data.get('time_delay', 0),
                strength=rel_data.get('strength', 1.0)
            )
            self.db.create_causality_relation(relation)
        
        return scenario

    def _generate_scenario_id(self) -> str:
        """生成唯一的场景 ID
        
        Returns:
            场景 ID
        """
        return f"scenario_{uuid.uuid4().hex[:8]}"

    def _extract_keywords(self, description: str) -> List[str]:
        """从场景描述中提取关键词
        
        使用简单的规则提取关键词：
        - 移除常见停用词
        - 提取名词性短语
        - 识别技术术语
        
        Args:
            description: 场景描述
            
        Returns:
            关键词列表
        """
        # 中文停用词
        chinese_stopwords = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
            '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
            '看', '好', '自己', '这', '那', '里', '就是', '可以', '这个', '能', '为',
            '与', '及', '等', '或', '但', '而', '因为', '所以', '如果', '那么'
        }
        
        # 英文停用词
        english_stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # 技术术语模式（保留这些）
        tech_patterns = [
            r'\b\w+[-_]\w+\b',  # server-01, user_id
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b',  # CamelCase
            r'\b\d+(?:\.\d+)*(?:GB|MB|KB|ms|s|%)\b',  # 数值单位
            r'\b(?:CPU|GPU|RAM|API|HTTP|HTTPS|SQL|JSON|YAML|XML)\b',  # 常见缩写
        ]
        
        keywords: Set[str] = set()
        
        # 提取技术术语
        for pattern in tech_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            keywords.update(matches)
        
        # 分词（简单的基于空格和标点的分词）
        # 支持中英文混合
        
        # 提取中文词（2个或更多连续中文字符）
        chinese_words = re.findall(r'[\u4e00-\u9fff]{2,}', description)
        for word in chinese_words:
            if word not in chinese_stopwords:
                keywords.add(word)
        
        # 提取英文单词和数字
        words = re.findall(r'[\w\-]+', description, re.UNICODE)
        
        for word in words:
            word_lower = word.lower()
            
            # 过滤停用词
            if word_lower in chinese_stopwords or word_lower in english_stopwords:
                continue
            
            # 过滤太短的词
            if len(word) < 2:
                continue
            
            # 保留有意义的词
            # 数字、英文单词（长度>=3）
            if word.isdigit() or (word.isalpha() and len(word) >= 3):
                keywords.add(word)
        
        return sorted(list(keywords))
