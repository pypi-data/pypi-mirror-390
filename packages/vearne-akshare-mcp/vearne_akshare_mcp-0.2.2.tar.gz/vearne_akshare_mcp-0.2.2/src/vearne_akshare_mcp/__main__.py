"""主入口文件"""

import argparse
import logging
from .core.mcp_server import create_mcp

def init_logger():
    """初始化日志"""
    logging.basicConfig(
        format="%(asctime)s %(name)s %(levelname)s %(message)s", 
        level=logging.INFO
    )

def main() -> None:
    """主函数"""
    init_logger()
    
    print("#### vearne_akshare_mcp ####")
    print("Project page: https://github.com/vearne/akshare-mcp")
    print("Author: <vearne> asdwoshiaotian@gmail.com")
    print("Version: 0.2.2")
    
    parser = argparse.ArgumentParser(
        description="An MCP server capable of retrieving A-share, Hong Kong stock, and U.S. stock data using AkShare."
    )
    parser.add_argument("--bind", default="127.0.0.1", help="Specify the IP address to bind to")
    parser.add_argument("--port", type=int, default=8902, help="Specify the port number")
    parser.add_argument("--http", action="store_true", help="Enable http server")
    parser.add_argument("--stateless", action="store_true", help="Enable stateless mode")
    
    args = parser.parse_args()
    
    mcp = create_mcp()
    if args.http:
        mcp.run(transport="streamable-http", host=args.bind, port=args.port, stateless_http=args.stateless)
    else:
        mcp.run()

if __name__ == "__main__":
    main()