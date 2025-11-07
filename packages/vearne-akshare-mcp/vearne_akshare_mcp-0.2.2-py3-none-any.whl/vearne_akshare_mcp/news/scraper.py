from playwright.sync_api import sync_playwright
from pydantic import Field
from typing import Annotated
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor


def get_cn_news(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None ,
            Field(description="Number of most recent records to return")
        ] = "50",
) -> str:
    """
        A股-获取个股新闻
        https://gu.qq.com/sh600690/gp/news
        https://gu.qq.com/sz000069/gp/news
    """
    symbol = symbol.lower()
    return get_news(symbol, recent_n)


def get_hk_news(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. '09633','00700')")],
        recent_n: Annotated[
            str | None,
            Field(description="Number of most recent records to return")
        ] = "50",
) -> str:
    """
        港股-获取个股新闻
        https://gu.qq.com/hk00700/gp/news
    """
    if not symbol.startswith("hk"):
        symbol = "hk" + symbol
    return get_news(symbol, recent_n)


def _get_news_sync(symbol: str, recent_n: str | None) -> str:
    """
        新闻来源: 腾讯
        同步版本的新闻获取函数
    """
    # 参数转换
    url_str = f"https://gu.qq.com/{symbol}/gp/news"
    logging.info(f"url_str:{url_str}")

    result = ""  # 初始化结果变量

    with sync_playwright() as p:
        # 启动浏览器（headless=True表示不显示浏览器界面）
        browser = p.chromium.launch(headless=True)

        # 创建上下文并设置请求头
        context = browser.new_context(
            # 设置更真实的用户代理和语言
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            locale='en-US,en;q=0.9',
            # 可以添加更多设备模拟参数
            viewport={'width': 1366, 'height': 768}
        )

        # 设置额外的HTTP头
        context.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'DNT': '1',  # 不要追踪
        })

        page = context.new_page()

        try:
            # 访问腾讯股票新闻页面
            page.goto(url_str, timeout=3000)

            # 等待页面加载完成（比固定sleep更好）
            page.wait_for_selector('.mod-detail', state='attached', timeout=5000)

            # 获取新闻列表（示例）
            news_items = page.query_selector_all('.mod-detail li')
            # print(f"找到 {len(news_items)} 条新闻")
            logging.info(f"找到 {len(news_items)} 条新闻")

            if recent_n is not None:
                recent_n = int(recent_n)
                news_items = news_items[:recent_n]

            ll = []
            for item in news_items:
                ll.append(item.inner_html())

            result = "\n".join(ll)

        except Exception as e:
            # print(f"发生错误: {e}")
            logging.error(f"发生错误: {e}")
        finally:
            # 关闭浏览器
            browser.close()
    return result  # 在finally块外返回结果

def get_news(
        symbol: Annotated[str, Field(description="Stock symbol (e.g. 'SH600519','SZ000025')")],
        recent_n: Annotated[
            str | None,
            Field(description="Number of most recent records to return")
        ] = "50",
) -> str:
    """
    安全地运行 Playwright 代码，无论是否在 asyncio 环境中
    """
    try:
        # 检查是否在 asyncio 事件循环中
        asyncio.get_running_loop()
        # 如果在事件循环中，使用线程池运行同步代码
        with ThreadPoolExecutor() as executor:
            future = executor.submit(_get_news_sync, symbol, recent_n)
            return future.result()
    except RuntimeError:
        # 没有事件循环，直接运行同步代码
        return _get_news_sync(symbol, recent_n)
