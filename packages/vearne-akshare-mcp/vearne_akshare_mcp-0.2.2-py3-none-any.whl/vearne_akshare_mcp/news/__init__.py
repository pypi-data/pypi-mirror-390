"""新闻模块"""

from .scraper import get_cn_news, get_hk_news
from .eastmoney import get_stock_news_em

__all__ = ["get_cn_news", "get_hk_news", "get_stock_news_em"]
