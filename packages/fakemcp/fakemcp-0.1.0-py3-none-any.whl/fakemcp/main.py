"""
Main entry point for FakeMCP server
"""

import asyncio
import sys
from fakemcp.config import Config
from fakemcp.database import Database
from fakemcp.mcp_server import get_server
from fakemcp.tools import ActorTools, DataTools, GuideTools, PersistenceTools, PlotTools, ScenarioTools
from fakemcp.logger import setup_default_logging, get_logger


def _create_handler(tool_instance, method_name):
    """创建工具处理器，避免闭包问题"""
    async def handler(args):
        method = getattr(tool_instance, method_name)
        return await method(**args)
    return handler


def register_all_tools():
    """注册所有 MCP 工具"""
    logger = get_logger(__name__)
    
    # 初始化数据库
    database = Database(Config.DATABASE_PATH)
    
    # 获取 MCP 服务器实例
    server = get_server()
    
    # 初始化工具集
    actor_tools = ActorTools(database)
    data_tools = DataTools(database)
    guide_tools = GuideTools(database)
    persistence_tools = PersistenceTools(database)
    plot_tools = PlotTools(database)
    scenario_tools = ScenarioTools(database)
    
    # 注册 guide 工具
    for tool_def in guide_tools.get_tool_definitions():
        server.register_tool(
            name=tool_def['name'],
            description=tool_def['description'],
            input_schema=tool_def['inputSchema'],
            handler=_create_handler(guide_tools, 'guide')
        )
        logger.info(f"Registered tool: {tool_def['name']}")
    
    # 注册 actor 工具
    for tool_def in actor_tools.get_tool_definitions():
        tool_name = tool_def['name']
        
        # 根据工具名称映射到对应的方法
        method_map = {
            'add_actor_config': 'add_actor_config',
            'remove_actor_config': 'remove_actor_config',
            'list_actors': 'list_actors'
        }
        
        if tool_name in method_map:
            server.register_tool(
                name=tool_name,
                description=tool_def['description'],
                input_schema=tool_def['inputSchema'],
                handler=_create_handler(actor_tools, method_map[tool_name])
            )
            logger.info(f"Registered tool: {tool_name}")
    
    # 注册 plot 工具
    for tool_def in plot_tools.get_tool_definitions():
        tool_name = tool_def['name']
        
        # 根据工具名称映射到对应的方法
        method_map = {
            'request_plot_expansion': 'request_plot_expansion',
            'add_causality_relation': 'add_causality_relation',
            'build_plot_graph': 'build_plot_graph',
            'validate_plot_consistency': 'validate_plot_consistency'
        }
        
        if tool_name in method_map:
            server.register_tool(
                name=tool_name,
                description=tool_def['description'],
                input_schema=tool_def['inputSchema'],
                handler=_create_handler(plot_tools, method_map[tool_name])
            )
            logger.info(f"Registered tool: {tool_name}")
    
    # 注册 scenario 工具
    for tool_def in scenario_tools.get_tool_definitions():
        tool_name = tool_def['name']
        
        # 根据工具名称映射到对应的方法
        method_map = {
            'set_scenario': 'set_scenario',
            'add_target_mcp': 'add_target_mcp',
            'get_scenario_status': 'get_scenario_status'
        }
        
        if tool_name in method_map:
            server.register_tool(
                name=tool_name,
                description=tool_def['description'],
                input_schema=tool_def['inputSchema'],
                handler=_create_handler(scenario_tools, method_map[tool_name])
            )
            logger.info(f"Registered tool: {tool_name}")
    
    # 注册 data 工具
    for tool_def in data_tools.get_tool_definitions():
        tool_name = tool_def['name']
        
        # 根据工具名称映射到对应的方法
        method_map = {
            'fetch_real_data': 'fetch_real_data',
            'generate_mock_data': 'generate_mock_data',
            'validate_mock_data': 'validate_mock_data'
        }
        
        if tool_name in method_map:
            server.register_tool(
                name=tool_name,
                description=tool_def['description'],
                input_schema=tool_def['inputSchema'],
                handler=_create_handler(data_tools, method_map[tool_name])
            )
            logger.info(f"Registered tool: {tool_name}")
    
    # 注册 persistence 工具
    for tool_def in persistence_tools.get_tool_definitions():
        tool_name = tool_def['name']
        
        # 根据工具名称映射到对应的方法
        method_map = {
            'save_scenario': 'save_scenario',
            'load_scenario': 'load_scenario'
        }
        
        if tool_name in method_map:
            server.register_tool(
                name=tool_name,
                description=tool_def['description'],
                input_schema=tool_def['inputSchema'],
                handler=_create_handler(persistence_tools, method_map[tool_name])
            )
            logger.info(f"Registered tool: {tool_name}")


async def shutdown(database: Database):
    """
    优雅关闭服务器
    
    Args:
        database: 数据库实例
    """
    logger = get_logger(__name__)
    logger.info("Shutting down FakeMCP server...")
    
    try:
        # 关闭数据库连接
        database.close()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


def main():
    """
    主入口函数
    
    初始化配置、日志、数据库，注册所有工具，并启动 MCP 服务器。
    处理优雅关闭和错误情况。
    
    Returns:
        int: 退出码（0 表示成功，1 表示失败）
    """
    try:
        # 验证配置
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        return 1
    
    # 确保必要的目录存在
    Config.ensure_directories()
    
    # 配置日志
    setup_default_logging()
    logger = get_logger(__name__)
    
    logger.info("=" * 60)
    logger.info(f"{Config.SERVER_NAME} v{Config.SERVER_VERSION}")
    logger.info(Config.SERVER_DESCRIPTION)
    logger.info("=" * 60)
    logger.info(f"Database: {Config.DATABASE_PATH}")
    logger.info(f"Cache: {Config.CACHE_DIR} (TTL: {Config.CACHE_TTL}s)")
    logger.info(f"Log Level: {Config.LOG_LEVEL}")
    logger.info("=" * 60)
    
    database = None
    
    try:
        logger.info("Initializing database...")
        database = Database(Config.DATABASE_PATH)
        
        logger.info("Registering MCP tools...")
        register_all_tools()
        
        logger.info("Starting MCP server...")
        server = get_server()
        asyncio.run(server.run())
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user (Ctrl+C)")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal server error: {e}", exc_info=True)
        return 1
        
    finally:
        # 优雅关闭
        if database:
            try:
                asyncio.run(shutdown(database))
            except Exception as e:
                logger.error(f"Error during shutdown: {e}", exc_info=True)
        
        logger.info("FakeMCP server stopped")


if __name__ == "__main__":
    sys.exit(main())
