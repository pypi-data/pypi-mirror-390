#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Facebook Scraper MCP 服务器
提供Facebook搜索相关功能的MCP工具集
"""

import os
import json
import asyncio
from typing import Any
import httpx
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# RapidAPI配置
RAPIDAPI_HOST = "facebook-scraper3.p.rapidapi.com"
RAPIDAPI_BASE_URL = f"https://{RAPIDAPI_HOST}"
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")

# 创建MCP服务器实例
server = Server("facebook-scraper")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    列出所有可用的Facebook搜索工具
    """
    return [
        types.Tool(
            name="search_locations",
            description="搜索Facebook位置信息。可以按关键词搜索地点、城市、国家等位置数据。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，例如城市名称、地点名称等"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="search_video",
            description="搜索Facebook视频。可以按关键词搜索相关视频内容。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="search_post",
            description="搜索Facebook帖子。可以按关键词搜索公开的帖子内容。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="search_place",
            description="搜索Facebook地点。可以搜索商家、景点、餐厅等地点信息。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="search_pages",
            description="搜索Facebook主页。可以搜索公司、品牌、公众人物等的Facebook主页。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="search_events",
            description="搜索Facebook活动。可以搜索公开的活动、聚会、会议等事件信息。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="search_groups_posts",
            description="搜索Facebook群组帖子。可以搜索公开群组中的帖子内容。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
        types.Tool(
            name="search_people",
            description="搜索Facebook用户。可以按姓名搜索Facebook公开用户资料。",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，例如人名"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回结果数量限制（可选）",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
        ),
    ]


async def call_facebook_api(endpoint: str, params: dict) -> dict:
    """
    调用Facebook Scraper API的通用函数
    
    Args:
        endpoint: API端点路径
        params: 查询参数
        
    Returns:
        API响应的JSON数据
    """
    if not RAPIDAPI_KEY:
        raise ValueError("未设置RAPIDAPI_KEY环境变量。请先设置您的RapidAPI密钥。")
    
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key": RAPIDAPI_KEY
    }
    
    url = f"{RAPIDAPI_BASE_URL}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {
                "error": f"API请求失败: {str(e)}",
                "status_code": getattr(e.response, "status_code", None) if hasattr(e, "response") else None
            }


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    处理工具调用请求
    """
    if not arguments:
        raise ValueError("缺少必需参数")
    
    query = arguments.get("query")
    if not query:
        raise ValueError("缺少必需参数: query")
    
    limit = arguments.get("limit", 10)
    
    # 根据工具名称映射到API端点（从RapidAPI页面获取的真实端点）
    endpoint_mapping = {
        "search_locations": "/search/locations",
        "search_video": "/search/videos",
        "search_post": "/search/posts",
        "search_place": "/search/places",
        "search_pages": "/search/pages",
        "search_events": "/search/events",
        "search_groups_posts": "/search/groups_posts",
        "search_people": "/search/people",
    }
    
    if name not in endpoint_mapping:
        raise ValueError(f"未知的工具: {name}")
    
    endpoint = endpoint_mapping[name]
    params = {
        "query": query,
        "limit": limit
    }
    
    # 调用API
    result = await call_facebook_api(endpoint, params)
    
    # 格式化返回结果
    return [
        types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )
    ]


async def main():
    """
    启动MCP服务器
    """
    # 检查API密钥
    if not RAPIDAPI_KEY:
        print("警告: 未设置RAPIDAPI_KEY环境变量", flush=True)
        print("请使用以下命令设置: export RAPIDAPI_KEY='your-api-key'", flush=True)
    
    # 使用stdio传输运行服务器
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="facebook-scraper",
                server_version="1.0.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run_server():
    """
    同步入口函数，用于命令行调用
    """
    asyncio.run(main())


if __name__ == "__main__":
    run_server()

