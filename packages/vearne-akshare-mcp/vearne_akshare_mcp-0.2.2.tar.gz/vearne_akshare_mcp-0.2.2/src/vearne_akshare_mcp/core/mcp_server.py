"""MCP服务器核心逻辑"""

from fastmcp import FastMCP
from fastmcp.tools.tool import FunctionTool
from .tools import get_datetime


def create_mcp() -> FastMCP:
    """创建并配置MCP服务器"""
    mcp = FastMCP(name="akshare-mcp")
    
    # 注册基础工具
    mcp.add_tool(FunctionTool.from_function(get_datetime))
    
    # 导入市场模块
    from ..markets import cn, hk, us
    from ..news import get_cn_news, get_hk_news, get_stock_news_em
    
    # 注册A股工具
    cn_tools = [
        cn.get_stock_profit_sheet_by_yearly_em,
        cn.get_stock_profit_sheet_by_quarterly_em,
        cn.get_stock_profit_sheet_by_report_em,
        cn.get_stock_cash_flow_sheet_by_yearly_em,
        cn.get_stock_cash_flow_sheet_by_quarterly_em,
        cn.get_stock_cash_flow_sheet_by_report_em,
        cn.get_stock_balance_sheet_by_yearly_em,
        cn.get_stock_balance_sheet_by_report_em,
        cn.get_stock_zh_a_hist,
        cn.get_stock_value_em,
        cn.calculate_value,
    ]
    for tool in cn_tools:
        mcp.add_tool(FunctionTool.from_function(tool))
    mcp.add_tool(FunctionTool.from_function(get_cn_news))
    
    # 注册港股工具
    hk_tools = [
        hk.get_stock_financial_hk_report_em,
        hk.get_stock_hk_hist,
    ]
    for tool in hk_tools:
        mcp.add_tool(FunctionTool.from_function(tool))
    mcp.add_tool(FunctionTool.from_function(get_hk_news))
    mcp.add_tool(FunctionTool.from_function(get_stock_news_em))
    
    # 注册美股工具
    us_tools = [
        us.get_stock_financial_us_report_em,
        us.get_stock_us_hist,
    ]
    for tool in us_tools:
        mcp.add_tool(FunctionTool.from_function(tool))
    
    return mcp
