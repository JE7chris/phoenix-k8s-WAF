FROM python:3.9-slim

WORKDIR /app

# 1. 替换阿里源 (保持之前的优化)
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

# 2. 🔥 核心修复：安装 libpcap 和 tcpdump
# supervisor: 进程管理
# libpcap-dev: Scapy 编译过滤器必需
# tcpdump: 包含很多抓包基础库，防万一
RUN apt-get update && apt-get install -y \
    supervisor \
    libpcap-dev \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# 3. 配置 Python 源
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

# 4. 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 配置文件与代码
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY . .

# 6. 启动
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
