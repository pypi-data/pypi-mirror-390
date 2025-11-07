"""
MCP Protocol Layer Implementation

This module implements the core MCP server functionality including:
- MCP protocol handshake and negotiation
- Tool registration mechanism
- Tool call routing
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from fakemcp.config import Config
from fakemcp.logger import get_logger
from fakemcp.errors import ToolNotFoundError, format_error_response


logger = get_logger(__name__)


@dataclass
class ToolHandler:
    """Tool handler configuration"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    

class MCPServer:
    """
    FakeMCP MCP 协议层
    
    实现 MCP 服务器的核心功能：
    - 协议握手和协商
    - 工具注册
    - 工具调用路由
    """
    
    def __init__(self):
        """初始化 MCP 服务器"""
        self.server = Server(Config.SERVER_NAME)
        self.tool_handlers: Dict[str, ToolHandler] = {}
        self._setup_handlers()
        
        logger.info(f"Initialized {Config.SERVER_NAME} v{Config.SERVER_VERSION}")
    
    def _setup_handlers(self):
        """设置 MCP 协议处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """
            列出所有可用的工具
            
            这是 MCP 协议的核心功能之一，客户端通过此接口
            发现服务器提供的所有工具
            """
            logger.debug(f"Listing {len(self.tool_handlers)} tools")
            
            tools = []
            for handler in self.tool_handlers.values():
                tool = Tool(
                    name=handler.name,
                    description=handler.description,
                    inputSchema=handler.input_schema
                )
                tools.append(tool)
            
            return tools
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """
            调用工具
            
            这是工具调用路由器，根据工具名称将请求路由到
            对应的处理器
            
            Args:
                name: 工具名称
                arguments: 工具参数
                
            Returns:
                工具执行结果
                
            Raises:
                ValueError: 工具不存在或执行失败
            """
            logger.info(f"Tool call: {name} with arguments: {arguments}")
            
            # 查找工具处理器
            handler = self.tool_handlers.get(name)
            if not handler:
                logger.error(f"Unknown tool: {name}")
                raise ToolNotFoundError(
                    message=f"Tool '{name}' is not registered",
                    tool_name=name
                )
            
            try:
                # 调用工具处理器
                result = await handler.handler(arguments)
                
                # 将结果转换为 TextContent
                # MCP 协议要求返回 Content 对象列表
                import json
                result_text = json.dumps(result, ensure_ascii=False, indent=2)
                
                logger.debug(f"Tool {name} executed successfully")
                return [TextContent(type="text", text=result_text)]
                
            except Exception as e:
                logger.error(f"Tool execution failed: {name} - {str(e)}", exc_info=True)
                
                # 使用统一的错误格式化
                error_result = format_error_response(e)
                
                import json
                return [TextContent(
                    type="text",
                    text=json.dumps(error_result, ensure_ascii=False, indent=2)
                )]
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ):
        """
        注册工具
        
        将工具添加到服务器的工具注册表中。工具必须在服务器
        启动前注册。
        
        Args:
            name: 工具名称（唯一标识符）
            description: 工具描述
            input_schema: JSON Schema 格式的输入参数定义
            handler: 工具处理函数（async callable）
            
        Example:
            >>> server.register_tool(
            ...     name="guide",
            ...     description="引导 AI Agent 完成场景构建",
            ...     input_schema={
            ...         "type": "object",
            ...         "properties": {
            ...             "action": {
            ...                 "type": "string",
            ...                 "enum": ["start", "next", "status", "reset"]
            ...             }
            ...         }
            ...     },
            ...     handler=guide_handler
            ... )
        """
        if name in self.tool_handlers:
            logger.warning(f"Tool {name} already registered, overwriting")
        
        tool_handler = ToolHandler(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler
        )
        
        self.tool_handlers[name] = tool_handler
        logger.info(f"Registered tool: {name}")
    
    def unregister_tool(self, name: str):
        """
        注销工具
        
        Args:
            name: 工具名称
        """
        if name in self.tool_handlers:
            del self.tool_handlers[name]
            logger.info(f"Unregistered tool: {name}")
        else:
            logger.warning(f"Tool {name} not found for unregistration")
    
    def get_registered_tools(self) -> List[str]:
        """
        获取已注册的工具列表
        
        Returns:
            工具名称列表
        """
        return list(self.tool_handlers.keys())
    
    async def run(self):
        """
        运行 MCP 服务器
        
        启动服务器并通过 stdio 与客户端通信。
        这是标准的 MCP 服务器运行模式。
        """
        logger.info(f"Starting {Config.SERVER_NAME} v{Config.SERVER_VERSION}")
        logger.info(f"Registered tools: {', '.join(self.get_registered_tools())}")
        
        # 使用 stdio 传输层运行服务器
        # 这是 MCP 协议的标准通信方式
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


# 全局服务器实例
_server_instance: Optional[MCPServer] = None


def get_server() -> MCPServer:
    """
    获取全局 MCP 服务器实例
    
    使用单例模式确保整个应用只有一个服务器实例
    
    Returns:
        MCPServer 实例
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = MCPServer()
    return _server_instance


def register_tool(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    handler: Callable
):
    """
    便捷函数：注册工具到全局服务器实例
    
    Args:
        name: 工具名称
        description: 工具描述
        input_schema: 输入参数 Schema
        handler: 工具处理函数
    """
    server = get_server()
    server.register_tool(name, description, input_schema, handler)


async def run_server():
    """
    便捷函数：运行全局服务器实例
    """
    server = get_server()
    await server.run()
