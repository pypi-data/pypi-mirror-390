"""
Workflow Guide Tool for FakeMCP

Provides the 'guide' MCP tool that guides AI agents through the
scenario building workflow by generating contextual prompts.
"""

from typing import Any, Dict, List, Optional

from fakemcp.database import Database
from fakemcp.workflow_guide import WorkflowGuide


class GuideTools:
    """工作流引导工具集"""

    def __init__(self, database: Database):
        """Initialize guide tools
        
        Args:
            database: Database instance for persistence
        """
        self.workflow_guide = WorkflowGuide(database)

    async def guide(
        self,
        action: Optional[str] = 'next'
    ) -> Dict[str, Any]:
        """引导 AI Agent 完成场景构建工作流
        
        MCP Tool: guide
        
        根据当前工作流阶段返回引导提示词，帮助 AI Agent 逐步完成：
        1. 收集目标 MCP 地址和场景描述
        2. 角色分析和创建
        3. 剧情深化
        4. 场景创建
        5. 生成模拟数据
        6. AI Agent 验证数据合理性
        7. 修正循环
        8. 用户最终确认
        9. 生成配置
        
        Args:
            action: 操作类型
                - 'start': 开始新的工作流
                - 'next': 获取当前阶段的引导（默认）
                - 'status': 查询当前状态
                - 'reset': 重置工作流
                
        Returns:
            引导信息，包含：
            - stage: 当前工作流阶段
            - prompt: 给 AI Agent 的引导提示词
            - nextActions: 建议的下一步操作列表
            - progress: 完成进度 (0-100)
            
        Example:
            >>> tools.guide(action='start')
            {
                'stage': 'init',
                'prompt': '请描述你想要模拟的测试场景...',
                'nextActions': ['set_scenario', 'add_target_mcp'],
                'progress': 0
            }
            
            >>> tools.guide(action='next')
            {
                'stage': 'actor_analysis',
                'prompt': '基于场景描述和 Schema 分析...',
                'nextActions': ['add_actor_config', 'advance to plot_deepening'],
                'progress': 33
            }
            
            >>> tools.guide(action='status')
            {
                'stage': 'data_generation',
                'prompt': '当前工作流阶段: data_generation',
                'nextActions': ['继续当前阶段的操作'],
                'progress': 66,
                'data': {...},
                'history': [...]
            }
        """
        try:
            # 验证 action 参数
            valid_actions = ['start', 'next', 'status', 'reset']
            if action not in valid_actions:
                return {
                    'success': False,
                    'error': {
                        'type': 'InvalidActionError',
                        'message': f'Invalid action: {action}. Must be one of: {", ".join(valid_actions)}',
                        'details': {
                            'action': action,
                            'valid_actions': valid_actions
                        },
                        'suggestions': [
                            'Use "start" to begin a new workflow',
                            'Use "next" to get guidance for the current stage',
                            'Use "status" to check current workflow state',
                            'Use "reset" to restart the workflow'
                        ]
                    }
                }
            
            # 生成引导提示
            result = self.workflow_guide.generate_prompt(action=action)
            
            # 添加成功标志
            result['success'] = True
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'type': 'GuideError',
                    'message': str(e),
                    'details': {
                        'action': action
                    },
                    'suggestions': [
                        'Check if the database is accessible',
                        'Try resetting the workflow with action="reset"'
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
                'name': 'guide',
                'description': (
                    '引导 AI Agent 完成场景构建工作流。'
                    '根据当前工作流阶段返回引导提示词，帮助逐步完成场景配置、'
                    '角色创建、剧情深化、数据生成和验证等步骤。'
                ),
                'inputSchema': {
                    'type': 'object',
                    'properties': {
                        'action': {
                            'type': 'string',
                            'description': '操作类型',
                            'enum': ['start', 'next', 'status', 'reset'],
                            'default': 'next'
                        }
                    }
                }
            }
        ]
