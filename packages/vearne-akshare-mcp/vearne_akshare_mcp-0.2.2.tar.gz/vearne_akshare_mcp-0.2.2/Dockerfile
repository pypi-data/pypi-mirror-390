FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    libwayland-client0 

RUN pip3 install playwright==1.55.0
RUN playwright install chromium --force
RUN pip3 install vearne-akshare-mcp==0.2.1

CMD ["/usr/local/bin/python3", "-m", "vearne_akshare_mcp", "--http", "--bind=0.0.0.0", "--port=8090"]
