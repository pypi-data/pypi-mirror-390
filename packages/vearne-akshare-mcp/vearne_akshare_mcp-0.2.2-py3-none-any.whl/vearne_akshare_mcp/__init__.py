"""
vearne_akshare_mcp - AkShare MCP Server
"""

__version__ = "0.1.9"
__author__ = "vearne"
__email__ = "asdwoshiaotian@gmail.com"

# 导出主要功能
from .core.mcp_server import create_mcp
from .markets import cn, hk, us
from .news import get_cn_news, get_hk_news

__all__ = [
    "create_mcp",
    "cn", "hk", "us", 
    "get_cn_news", "get_hk_news"
]