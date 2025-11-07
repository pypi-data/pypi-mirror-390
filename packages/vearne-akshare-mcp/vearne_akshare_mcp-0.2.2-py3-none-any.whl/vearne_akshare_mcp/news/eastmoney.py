# 数据来源: 东方财富
from typing import Annotated
from pydantic import Field
import akshare as ak

def get_stock_news_em(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. '600519','00700')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "50",
) -> str:
    """
        东方财富-个股新闻-最近 100 条新闻
        https://so.eastmoney.com/news/s?keyword=603777
    """
    df = ak.stock_news_em(symbol=symbol)
    if recent_n is not None:
        recent_n = int(recent_n)
        df = df.head(recent_n)
    return df.to_json(orient="records", double_precision=3, force_ascii=False)


