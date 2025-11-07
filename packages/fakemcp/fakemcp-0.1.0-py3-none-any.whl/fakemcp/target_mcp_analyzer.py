"""
Target MCP Analyzer - 分析和连接真实的 MCP 服务器
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from fakemcp.config import Config
from fakemcp.database import Database
from fakemcp.models import TargetMCP
from fakemcp.logger import get_logger
from fakemcp.errors import ConnectionError, SchemaError, TargetMCPNotFoundError


logger = get_logger(__name__)


class TargetMCPAnalyzer:
    """目标 MCP 分析器
    
    负责连接到真实的 MCP 服务器，获取 Schema，识别角色字段，
    调用真实服务器获取示例数据，并实现缓存机制。
    """
    
    # 常见的角色字段名称模式
    ACTOR_FIELD_PATTERNS = [
        r'.*_id$',          # 以 _id 结尾: server_id, user_id, resource_id
        r'^instance.*',     # 以 instance 开头: instance, instance_id
        r'^host.*',         # 以 host 开头: host, hostname
        r'^server.*',       # 以 server 开头: server, server_id
        r'^user.*',         # 以 user 开头: user, user_id
        r'^resource.*',     # 以 resource 开头: resource, resource_id
        r'^city.*',         # 以 city 开头: city, city_name
        r'^location.*',     # 以 location 开头: location, location_id
        r'^job$',           # 精确匹配: job
        r'^application$',   # 精确匹配: application
        r'^service$',       # 精确匹配: service
    ]
    
    # 排除的字段名称（即使匹配模式也不应该被识别为角色字段）
    EXCLUDED_FIELD_NAMES = [
        'metric_name', 'field_name', 'column_name', 'table_name',
        'database_name', 'file_name', 'path_name', 'key_name',
        'value_name', 'type_name', 'class_name', 'method_name'
    ]
    
    def __init__(self, database: Database):
        """初始化分析器
        
        Args:
            database: 数据库实例
        """
        self.db = database
        self.cache_dir = Path(Config.CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self):
        """关闭 HTTP 客户端"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def connect(
        self,
        target_id: str,
        name: str,
        url: str,
        config: Optional[Dict[str, Any]] = None
    ) -> TargetMCP:
        """连接到目标 MCP 服务器并获取 Schema
        
        Args:
            target_id: 目标 MCP 的唯一标识
            name: 目标 MCP 的名称
            url: 目标 MCP 的 URL
            config: 可选的连接配置（如认证信息）
        
        Returns:
            TargetMCP 对象
        
        Raises:
            ConnectionError: 连接失败
            ValueError: Schema 解析失败
        """
        logger.info(f"Connecting to target MCP: {name} at {url}")
        
        if config is None:
            config = {}
        
        # 尝试获取 Schema
        try:
            schema = await self.get_schema(url, config)
        except Exception as e:
            logger.error(f"Failed to connect to {url}: {str(e)}")
            raise ConnectionError(
                message=f"Failed to connect to target MCP server",
                url=url,
                details={"original_error": str(e)}
            )
        
        # 识别角色字段
        actor_fields = self.identify_actor_fields(schema)
        
        # 创建 TargetMCP 对象
        target_mcp = TargetMCP(
            id=target_id,
            name=name,
            url=url,
            config=config,
            schema=schema,
            actor_fields=actor_fields,
            example_data={},
            connected=True
        )
        
        # 保存到数据库
        existing = self.db.get_target_mcp(target_id)
        if existing:
            self.db.update_target_mcp(target_mcp)
        else:
            self.db.create_target_mcp(target_mcp)
        
        # 缓存 Schema
        self._cache_schema(target_id, schema)
        
        return target_mcp
    
    async def get_schema(
        self,
        url: str,
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """获取目标 MCP 服务器的 Schema
        
        Args:
            url: MCP 服务器 URL
            config: 连接配置
        
        Returns:
            Schema 字典，包含 tools 列表
        
        Raises:
            httpx.HTTPError: HTTP 请求失败
            ValueError: Schema 格式无效
        """
        client = await self._get_http_client()
        
        # 准备请求头
        headers = {"Content-Type": "application/json"}
        if config and "auth_token" in config:
            headers["Authorization"] = f"Bearer {config['auth_token']}"
        
        # 发送 MCP 协议的 tools/list 请求
        # 注意：这里假设标准的 MCP JSON-RPC 格式
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        try:
            response = await client.post(url, json=request_data, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # 验证响应格式
            if "result" not in result:
                logger.error("Invalid MCP response: missing 'result' field")
                raise SchemaError(
                    message="Invalid MCP response format",
                    schema_source=url,
                    details={"missing_field": "result"}
                )
            
            if "tools" not in result["result"]:
                logger.error("Invalid MCP schema: missing 'tools' field")
                raise SchemaError(
                    message="Invalid MCP schema format",
                    schema_source=url,
                    details={"missing_field": "tools"}
                )
            
            return result["result"]
            
        except httpx.HTTPError as e:
            raise httpx.HTTPError(f"Failed to fetch schema from {url}: {str(e)}")
    
    def identify_actor_fields(self, schema: Dict[str, Any]) -> List[str]:
        """识别 Schema 中的潜在角色字段
        
        通过分析工具参数名称，识别可能代表角色实体的字段。
        
        Args:
            schema: MCP Schema 字典
        
        Returns:
            角色字段名称列表
        """
        actor_fields = set()
        
        tools = schema.get("tools", [])
        
        for tool in tools:
            # 获取输入参数 Schema
            input_schema = tool.get("inputSchema", {})
            properties = input_schema.get("properties", {})
            
            # 检查每个参数
            for param_name, param_info in properties.items():
                # 检查参数名是否匹配角色字段模式
                if self._is_actor_field(param_name):
                    actor_fields.add(param_name)
                
                # 检查参数描述中是否包含角色相关关键词
                description = param_info.get("description", "").lower()
                if any(keyword in description for keyword in [
                    "identifier", "id", "name", "instance", "entity",
                    "resource", "server", "host", "user", "location"
                ]):
                    actor_fields.add(param_name)
        
        return sorted(list(actor_fields))
    
    def _is_actor_field(self, field_name: str) -> bool:
        """检查字段名是否匹配角色字段模式
        
        Args:
            field_name: 字段名称
        
        Returns:
            是否为角色字段
        """
        field_lower = field_name.lower()
        
        # 首先检查是否在排除列表中
        if field_lower in self.EXCLUDED_FIELD_NAMES:
            return False
        
        # 然后检查是否匹配角色字段模式
        for pattern in self.ACTOR_FIELD_PATTERNS:
            if re.match(pattern, field_lower):
                return True
        
        return False
    
    async def fetch_real_data(
        self,
        target_id: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """从真实 MCP 服务器获取示例数据
        
        Args:
            target_id: 目标 MCP ID
            tool_name: 工具名称
            parameters: 调用参数
        
        Returns:
            真实返回数据
        
        Raises:
            ValueError: 目标 MCP 不存在
            httpx.HTTPError: HTTP 请求失败
        """
        # 检查缓存
        cached_data = self._get_cached_data(target_id, tool_name, parameters)
        if cached_data is not None:
            return cached_data
        
        # 从数据库获取目标 MCP
        target_mcp = self.db.get_target_mcp(target_id)
        if not target_mcp:
            logger.error(f"Target MCP not found: {target_id}")
            raise TargetMCPNotFoundError(
                message=f"Target MCP '{target_id}' not found",
                target_id=target_id
            )
        
        # 调用真实 MCP
        client = await self._get_http_client()
        
        headers = {"Content-Type": "application/json"}
        if target_mcp.config.get("auth_token"):
            headers["Authorization"] = f"Bearer {target_mcp.config['auth_token']}"
        
        request_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": parameters
            }
        }
        
        try:
            response = await client.post(
                target_mcp.url,
                json=request_data,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            
            if "result" not in result:
                logger.error("Invalid MCP response: missing 'result' field")
                raise SchemaError(
                    message="Invalid MCP response format",
                    details={"missing_field": "result", "tool": tool_name}
                )
            
            data = result["result"]
            
            # 缓存数据
            self._cache_data(target_id, tool_name, parameters, data)
            
            # 更新 example_data
            if tool_name not in target_mcp.example_data:
                target_mcp.example_data[tool_name] = []
            target_mcp.example_data[tool_name].append({
                "parameters": parameters,
                "response": data
            })
            self.db.update_target_mcp(target_mcp)
            
            return data
            
        except httpx.HTTPError as e:
            raise httpx.HTTPError(
                f"Failed to fetch data from {target_mcp.url}: {str(e)}"
            )
    
    def _cache_schema(self, target_id: str, schema: Dict[str, Any]) -> None:
        """缓存 Schema 到文件系统
        
        Args:
            target_id: 目标 MCP ID
            schema: Schema 数据
        """
        cache_file = self.cache_dir / f"{target_id}_schema.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
    
    def _get_cached_schema(self, target_id: str) -> Optional[Dict[str, Any]]:
        """从缓存获取 Schema
        
        Args:
            target_id: 目标 MCP ID
        
        Returns:
            Schema 数据，如果不存在则返回 None
        """
        cache_file = self.cache_dir / f"{target_id}_schema.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _cache_data(
        self,
        target_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        data: Any
    ) -> None:
        """缓存示例数据到文件系统
        
        Args:
            target_id: 目标 MCP ID
            tool_name: 工具名称
            parameters: 调用参数
            data: 返回数据
        """
        # 创建缓存键（基于参数的哈希）
        param_str = json.dumps(parameters, sort_keys=True)
        cache_key = f"{target_id}_{tool_name}_{hash(param_str)}"
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        cache_entry = {
            "target_id": target_id,
            "tool_name": tool_name,
            "parameters": parameters,
            "data": data
        }
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_entry, f, indent=2, ensure_ascii=False)
    
    def _get_cached_data(
        self,
        target_id: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Optional[Any]:
        """从缓存获取示例数据
        
        Args:
            target_id: 目标 MCP ID
            tool_name: 工具名称
            parameters: 调用参数
        
        Returns:
            缓存的数据，如果不存在则返回 None
        """
        param_str = json.dumps(parameters, sort_keys=True)
        cache_key = f"{target_id}_{tool_name}_{hash(param_str)}"
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)
                return cache_entry.get("data")
        
        return None
    
    def clear_cache(self, target_id: Optional[str] = None) -> None:
        """清除缓存
        
        Args:
            target_id: 如果指定，只清除该目标的缓存；否则清除所有缓存
        """
        if target_id:
            # 清除特定目标的缓存
            pattern = f"{target_id}_*"
            for cache_file in self.cache_dir.glob(pattern):
                cache_file.unlink()
        else:
            # 清除所有缓存
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
