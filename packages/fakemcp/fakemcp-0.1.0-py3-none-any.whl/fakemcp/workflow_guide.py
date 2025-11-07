"""
Workflow Guide for FakeMCP

Manages the workflow state and generates prompts to guide AI agents
through the scenario building process.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fakemcp.database import Database
from fakemcp.models import WorkflowState


class WorkflowGuide:
    """工作流引导 - 管理场景构建的工作流状态并生成引导提示"""

    # 工作流阶段定义
    STAGE_INIT = 'init'
    STAGE_TARGET_COLLECTION = 'target_collection'
    STAGE_ACTOR_ANALYSIS = 'actor_analysis'
    STAGE_PLOT_DEEPENING = 'plot_deepening'
    STAGE_SCENARIO_CREATION = 'scenario_creation'
    STAGE_DATA_GENERATION = 'data_generation'
    STAGE_VALIDATION = 'validation'
    STAGE_CORRECTION = 'correction'
    STAGE_COMPLETED = 'completed'

    # 阶段顺序
    STAGE_ORDER = [
        STAGE_INIT,
        STAGE_TARGET_COLLECTION,
        STAGE_ACTOR_ANALYSIS,
        STAGE_PLOT_DEEPENING,
        STAGE_SCENARIO_CREATION,
        STAGE_DATA_GENERATION,
        STAGE_VALIDATION,
        STAGE_CORRECTION,
        STAGE_COMPLETED
    ]

    def __init__(self, database: Database):
        """Initialize workflow guide
        
        Args:
            database: Database instance for persistence
        """
        self.db = database

    def start_workflow(self) -> WorkflowState:
        """开始新的工作流
        
        Returns:
            初始化的 WorkflowState
        """
        state = WorkflowState(
            stage=self.STAGE_INIT,
            data={},
            history=[],
            plot_suggestions=[]
        )
        
        self._add_history_entry(state, 'workflow_started', 'Workflow initialized')
        self.db.save_workflow_state(state)
        
        return state

    def get_current_state(self) -> Optional[WorkflowState]:
        """获取当前工作流状态
        
        Returns:
            当前的 WorkflowState，如果不存在则返回 None
        """
        return self.db.get_workflow_state()

    def advance_stage(self, data_updates: Optional[Dict[str, Any]] = None) -> Optional[WorkflowState]:
        """推进到下一个工作流阶段
        
        Args:
            data_updates: 要更新的数据（可选）
            
        Returns:
            更新后的 WorkflowState，如果无法推进则返回 None
        """
        state = self.db.get_workflow_state()
        if not state:
            return None
        
        # 获取当前阶段索引
        try:
            current_index = self.STAGE_ORDER.index(state.stage)
        except ValueError:
            return None
        
        # 检查是否已完成
        if current_index >= len(self.STAGE_ORDER) - 1:
            return state
        
        # 推进到下一阶段
        next_stage = self.STAGE_ORDER[current_index + 1]
        state.stage = next_stage
        
        # 更新数据
        if data_updates:
            state.data.update(data_updates)
        
        self._add_history_entry(state, 'stage_advanced', f'Advanced to stage: {next_stage}')
        self.db.save_workflow_state(state)
        
        return state

    def update_data(self, updates: Dict[str, Any]) -> Optional[WorkflowState]:
        """更新工作流数据
        
        Args:
            updates: 要更新的数据
            
        Returns:
            更新后的 WorkflowState，如果不存在则返回 None
        """
        state = self.db.get_workflow_state()
        if not state:
            return None
        
        state.data.update(updates)
        self._add_history_entry(state, 'data_updated', f'Updated data: {list(updates.keys())}')
        self.db.save_workflow_state(state)
        
        return state

    def add_plot_suggestion(self, suggestion: Dict[str, Any]) -> Optional[WorkflowState]:
        """添加剧情扩展建议
        
        Args:
            suggestion: 剧情建议
            
        Returns:
            更新后的 WorkflowState，如果不存在则返回 None
        """
        state = self.db.get_workflow_state()
        if not state:
            return None
        
        state.plot_suggestions.append(suggestion)
        self._add_history_entry(state, 'plot_suggestion_added', f'Added plot suggestion')
        self.db.save_workflow_state(state)
        
        return state

    def reset_workflow(self) -> None:
        """重置工作流状态"""
        self.db.clear_workflow_state()

    def get_progress(self) -> int:
        """获取工作流进度（0-100）
        
        Returns:
            进度百分比
        """
        state = self.db.get_workflow_state()
        if not state:
            return 0
        
        try:
            current_index = self.STAGE_ORDER.index(state.stage)
            total_stages = len(self.STAGE_ORDER)
            return int((current_index / (total_stages - 1)) * 100)
        except (ValueError, ZeroDivisionError):
            return 0

    def generate_prompt(self, action: str = 'next') -> Dict[str, Any]:
        """生成当前阶段的引导提示
        
        Args:
            action: 操作类型 ('start', 'next', 'status', 'reset')
            
        Returns:
            包含 stage, prompt, nextActions, progress 的字典
        """
        if action == 'start':
            state = self.start_workflow()
        elif action == 'reset':
            self.reset_workflow()
            state = self.start_workflow()
        else:
            state = self.db.get_workflow_state()
            if not state:
                state = self.start_workflow()
        
        if action == 'status':
            return self._generate_status_response(state)
        
        # 根据当前阶段生成提示
        prompt_generator = {
            self.STAGE_INIT: self._generate_init_prompt,
            self.STAGE_TARGET_COLLECTION: self._generate_target_collection_prompt,
            self.STAGE_ACTOR_ANALYSIS: self._generate_actor_analysis_prompt,
            self.STAGE_PLOT_DEEPENING: self._generate_plot_deepening_prompt,
            self.STAGE_SCENARIO_CREATION: self._generate_scenario_creation_prompt,
            self.STAGE_DATA_GENERATION: self._generate_data_generation_prompt,
            self.STAGE_VALIDATION: self._generate_validation_prompt,
            self.STAGE_CORRECTION: self._generate_correction_prompt,
            self.STAGE_COMPLETED: self._generate_completed_prompt
        }
        
        generator = prompt_generator.get(state.stage, self._generate_default_prompt)
        return generator(state)

    def _generate_init_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成初始化阶段的提示"""
        prompt = """请描述你想要模拟的测试场景，并提供需要模拟的 MCP 服务器信息。

例如：
- 场景: "模拟内存泄露场景"
- 目标 MCP: Prometheus (http://...), CloudMonitoring (http://...), Logging (http://...)

请使用 set_scenario 和 add_target_mcp 工具来配置场景。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['set_scenario', 'add_target_mcp'],
            'progress': self.get_progress()
        }

    def _generate_target_collection_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成目标收集阶段的提示"""
        target_mcps = state.data.get('target_mcps', [])
        actor_fields = state.data.get('actor_fields', {})
        
        prompt = f"""正在分析目标 MCP 服务器...

已添加的目标 MCP: {len(target_mcps)} 个
"""
        
        if actor_fields:
            prompt += "\n已识别的潜在角色字段:\n"
            for mcp_id, fields in actor_fields.items():
                prompt += f"- {mcp_id}: {', '.join(fields)}\n"
        
        prompt += """
请为每个目标 MCP 提供至少一组真实的调用参数示例，以便获取真实返回数据。
使用 fetch_real_data 工具。

完成后，我们将进入角色分析阶段。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['fetch_real_data', 'advance to actor_analysis'],
            'progress': self.get_progress()
        }

    def _generate_actor_analysis_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成角色分析阶段的提示"""
        scenario_desc = state.data.get('scenario_description', '未设置')
        actor_fields = state.data.get('actor_fields', {})
        
        prompt = f"""基于场景描述和 Schema 分析，现在需要创建角色配置。

场景描述: {scenario_desc}

"""
        
        if actor_fields:
            prompt += "建议的角色类型:\n"
            for mcp_id, fields in actor_fields.items():
                prompt += f"- {', '.join(fields)} (来自 {mcp_id})\n"
            prompt += "\n"
        
        prompt += """请为每个角色添加场景配置，描述该角色在场景中的行为。

例如:
- actor_type: "server_id", actor_id: "server-01", description: "内存持续增长，从 2GB 增长到 8GB"
- actor_type: "server_id", actor_id: "server-02", description: "内存正常，保持在 1GB 左右"

使用 add_actor_config 工具添加角色配置。

完成后，我们将进入剧情深化阶段。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['add_actor_config', 'advance to plot_deepening'],
            'progress': self.get_progress()
        }

    def _generate_plot_deepening_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成剧情深化阶段的提示"""
        actors = state.data.get('actors', [])
        target_mcps = state.data.get('target_mcps', [])
        main_event = state.data.get('main_event', '场景中的主要事件')
        
        prompt = f"""角色配置完成。现在让我们深化剧情，探索事件的根本原因和影响链。

当前主要事件: {main_event}
已有角色: {', '.join(actors) if actors else '无'}
目标 MCP: {', '.join(target_mcps) if target_mcps else '无'}

使用 request_plot_expansion 工具获取剧情扩展提示。AI IDE 将帮助你分析可能的：
- 根本原因 (root_cause): 导致当前事件的原因
- 副作用 (side_effect): 当前事件导致的后果
- 相关事件 (related_event): 同时发生的其他事件

根据 AI 的建议，使用 add_causality_relation 工具建立因果关系。

完成剧情构建后，我们将进入场景创建阶段。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['request_plot_expansion', 'add_causality_relation', 'advance to scenario_creation'],
            'progress': self.get_progress()
        }

    def _generate_scenario_creation_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成场景创建阶段的提示"""
        causality_count = state.data.get('causality_relations_count', 0)
        
        prompt = f"""剧情构建完成（已建立 {causality_count} 个因果关系）。

现在使用 build_plot_graph 生成剧情图，这将：
1. 构建完整的剧情图结构
2. 生成时间线
3. 验证因果关系的一致性

然后使用 validate_plot_consistency 验证剧情的逻辑一致性：
- 检测循环依赖
- 验证时间线冲突
- 确认所有角色已配置

验证通过后，我们将进入数据生成阶段。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['build_plot_graph', 'validate_plot_consistency', 'advance to data_generation'],
            'progress': self.get_progress()
        }

    def _generate_data_generation_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成数据生成阶段的提示"""
        plot_nodes = state.data.get('plot_nodes_count', 0)
        
        prompt = f"""正在根据剧情图生成模拟数据...

剧情图包含 {plot_nodes} 个事件节点。

FakeMCP 将根据：
- 角色配置
- 因果关系
- 时间线
- 目标 MCP 的 Schema

生成逻辑一致的模拟数据。

使用 generate_mock_data 工具为每个目标 MCP 生成数据。

生成完成后，我们将进入验证阶段。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['generate_mock_data', 'advance to validation'],
            'progress': self.get_progress()
        }

    def _generate_validation_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成验证阶段的提示"""
        generated_data_count = state.data.get('generated_data_count', 0)
        
        prompt = f"""数据生成完成（已生成 {generated_data_count} 组数据）。

现在需要验证数据的合理性：
- Schema 一致性
- 时间戳对齐
- 因果关系体现
- 数值合理性

使用 validate_mock_data 工具验证生成的数据。

如果发现问题，我们将进入修正阶段。
如果验证通过，场景构建完成。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['validate_mock_data', 'advance to correction or completed'],
            'progress': self.get_progress()
        }

    def _generate_correction_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成修正阶段的提示"""
        issues = state.data.get('validation_issues', [])
        
        prompt = """数据验证发现问题，需要修正：

"""
        
        if issues:
            for i, issue in enumerate(issues, 1):
                prompt += f"{i}. {issue}\n"
        else:
            prompt += "（具体问题请查看验证结果）\n"
        
        prompt += """
根据验证建议，你可以：
1. 调整角色配置（使用 add_actor_config 更新）
2. 修改因果关系（使用 add_causality_relation）
3. 重新生成数据（使用 generate_mock_data）

修正后，返回验证阶段重新验证。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['adjust configuration', 'regenerate data', 'return to validation'],
            'progress': self.get_progress()
        }

    def _generate_completed_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成完成阶段的提示"""
        scenario_id = state.data.get('scenario_id', 'unknown')
        
        prompt = f"""🎉 场景构建完成！

场景 ID: {scenario_id}

你现在可以：
1. 使用 save_scenario 保存配置以便后续使用
2. 开始使用 generate_mock_data 获取模拟数据
3. 在 AI IDE 中测试你的 Agent

FakeMCP 已准备好响应对目标 MCP 的调用。当 AI Agent 调用目标 MCP 时，FakeMCP 将根据场景配置返回相应的模拟数据。

如需构建新场景，使用 guide 工具的 'reset' 操作。"""

        return {
            'stage': state.stage,
            'prompt': prompt,
            'nextActions': ['save_scenario', 'test with AI Agent', 'reset workflow'],
            'progress': 100
        }

    def _generate_default_prompt(self, state: WorkflowState) -> Dict[str, Any]:
        """生成默认提示（未知阶段）"""
        return {
            'stage': state.stage,
            'prompt': f'当前阶段: {state.stage}。使用 guide 工具获取下一步指引。',
            'nextActions': ['guide'],
            'progress': self.get_progress()
        }

    def _generate_status_response(self, state: WorkflowState) -> Dict[str, Any]:
        """生成状态查询响应"""
        return {
            'stage': state.stage,
            'prompt': f'当前工作流阶段: {state.stage}',
            'nextActions': ['继续当前阶段的操作'],
            'progress': self.get_progress(),
            'data': state.data,
            'history': state.history[-5:] if len(state.history) > 5 else state.history  # 最近5条历史
        }

    def _add_history_entry(self, state: WorkflowState, event_type: str, description: str) -> None:
        """添加历史记录条目
        
        Args:
            state: 工作流状态
            event_type: 事件类型
            description: 事件描述
        """
        entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'description': description,
            'stage': state.stage
        }
        state.history.append(entry)
