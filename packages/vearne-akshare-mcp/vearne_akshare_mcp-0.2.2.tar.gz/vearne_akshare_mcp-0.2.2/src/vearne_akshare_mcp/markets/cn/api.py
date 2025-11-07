import akshare as ak
from pydantic import Field
from typing import Annotated, Literal
import json
import time

def get_stock_profit_sheet_by_yearly_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-利润表-按年度
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_profit_sheet_by_yearly_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    return df.to_json(orient="records", double_precision=3, force_ascii=False)


def get_stock_profit_sheet_by_quarterly_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-利润表-按单季度
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_profit_sheet_by_quarterly_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    df = df[[
        "SECUCODE", "REPORT_DATE_NAME", "TOTAL_OPERATE_INCOME", "OPERATE_COST", "RESEARCH_EXPENSE", "SALE_EXPENSE",
        "MANAGE_EXPENSE", "FINANCE_EXPENSE", "INVEST_INCOME", "OPERATE_PROFIT", "TOTAL_PROFIT",
        "NETPROFIT", "PARENT_NETPROFIT", "DEDUCT_PARENT_NETPROFIT", "BASIC_EPS"]]
    return df.to_json(orient="records", double_precision=3, force_ascii=False)

def get_stock_profit_sheet_by_report_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-利润表-报告期
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    return df.to_json(orient="records", double_precision=3, force_ascii=False)


def get_stock_cash_flow_sheet_by_yearly_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-现金流量表-按年度
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_cash_flow_sheet_by_yearly_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    return df.to_json(orient="records", double_precision=3, force_ascii=False)


def get_stock_cash_flow_sheet_by_quarterly_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-现金流量表-按单季度
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_cash_flow_sheet_by_quarterly_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    df = df[["SECUCODE", "REPORT_DATE_NAME", "TOTAL_OPERATE_INFLOW", "TOTAL_OPERATE_OUTFLOW", "NETCASH_OPERATE",
             "TOTAL_INVEST_INFLOW", "TOTAL_INVEST_OUTFLOW", "NETCASH_INVEST", "TOTAL_FINANCE_INFLOW",
             "TOTAL_FINANCE_OUTFLOW", "NETCASH_FINANCE", "CCE_ADD", "BEGIN_CCE", "END_CCE"]]
    return df.to_json(orient="records", double_precision=3, force_ascii=False)

def get_stock_cash_flow_sheet_by_report_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-现金流量表-按报告期
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    return df.to_json(orient="records", double_precision=3, force_ascii=False)

def get_stock_balance_sheet_by_yearly_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-资产负债表-按年度
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_balance_sheet_by_yearly_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    return df.to_json(orient="records", double_precision=3, force_ascii=False)


def get_stock_balance_sheet_by_report_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "10",
) -> str:
    """
        A股
        东方财富-股票-财务分析-资产负债表-按报告期
        https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code=sh600519#lrb-0
    """
    df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    df = df[["SECUCODE", "TOTAL_ASSETS", "TOTAL_LIABILITIES", "TOTAL_EQUITY", "TOTAL_PARENT_EQUITY", "MONETARYFUNDS",
             "TOTAL_CURRENT_ASSETS", "TOTAL_CURRENT_LIAB", "TOTAL_ASSETS_YOY", "TOTAL_LIABILITIES_YOY",
             "TOTAL_PARENT_EQUITY_YOY", "MONETARYFUNDS_YOY", "FIXED_ASSET_YOY", "INVENTORY_YOY", "SHORT_LOAN",
             "LONG_LOAN", "SHORT_LOAN_YOY", "LONG_LOAN_YOY", "CURRENT_RATIO", "ACCOUNTS_RECE", "ACCOUNTS_PAYABLE",
             "INVENTORY", "ACCOUNTS_RECE_YOY", "ACCOUNTS_PAYABLE_YOY", "UNASSIGN_RPOFIT", "CAPITAL_RESERVE",
             "SURPLUS_RESERVE", "UNASSIGN_RPOFIT_YOY"]]
    return df.to_json(orient="records", double_precision=3, force_ascii=False)

def get_stock_zh_a_hist(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. '600519','000025')")],
        start_date: Annotated[str, Field(description="start date (e.g. '20201103')")],
        end_date: Annotated[str, Field(description="end date (e.g. '20251103')")],
        adjust: Annotated[str, Literal["qfq", "hfq", "hfq-factor", "qfq-factor", ""],
        Field(description="默认为空: 返回不复权的数据; qfq: 返回前复权后的数据; hfq: 返回后复权后的数据; hfq-factor: 返回后复权因子; qfq-factor: 返回前复权因子")],
) -> str:
    """
        A股
        东方财富网-行情首页-沪深京 A 股-每日行情
        https://quote.eastmoney.com/concept/sh603777.html?from=classic
    """
    df = ak.stock_zh_a_hist(symbol=symbol, start_date=start_date, end_date=end_date, adjust=adjust)
    return df.to_json(orient="records", double_precision=3, force_ascii=False)

def get_stock_value_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. '600519','000025')")],
) -> str:
    """
        A股
        东方财富网-数据中心-估值分析-每日互动-每日互动-估值分析
        https://data.eastmoney.com/gzfx/detail/300766.html
    """
    df = ak.stock_value_em(symbol=symbol)
    # 选择需要的列并重命名
    df = df[["数据日期", "PEG值", "市净率", "PE(静)", "PE(TTM)", "市现率", "市销率"]]
    df = df.rename(columns={
        "数据日期": "date",
        "PEG值": "peg",
        "市净率": "pb",
        "PE(静)": "pe_static",
        "PE(TTM)": "pe_ttm",
        "市现率": "pcf",
        "市销率": "ps"
    })
    return df.to_json(orient="records", double_precision=3, force_ascii=False)

def calculate_value(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. '600519','000025')")],
) -> str:
    """
        根据近5年的数据计算PE、PB的百分位
    """
    s = get_stock_value_em(symbol)
    ll = json.loads(s)

    # 获取当前时间戳（毫秒）
    current_time_ms = int(time.time() * 1000)
    # 计算 5 年前的时间戳（毫秒）
    five_years_ago_ms = current_time_ms - (5 * 365 * 24 * 60 * 60 * 1000)

    # 筛选最近 5 年的数据
    ll = [item for item in ll if item["date"] >= five_years_ago_ms]

    last_record = ll[len(ll)-1]
    result = last_record.copy()
    # 1.计算市盈率百分位
    # 按照 pe_ttm 排序
    sorted_data = sorted(ll, key=lambda x: x['pe_ttm'])
    for index, item in enumerate(sorted_data):
        if last_record["pe_ttm"] <= item["pe_ttm"] :
            result["pe_percent"] = "{:.2f}%".format(index/len(ll) * 100)
            break

    # 2.计算市净率百分位
    sorted_data = sorted(ll, key=lambda x: x['pb'])
    for index, item in enumerate(sorted_data):
        if last_record["pb"] <= item["pb"] :
            result["pb_percent"] = "{:.2f}%".format(index/len(ll) * 100)
            break
    return json.dumps(result)