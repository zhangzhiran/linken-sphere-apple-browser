# Linken Sphere Apple Browser - Linux构建容器
FROM python:3.10-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制文件
COPY . .

# 安装Python依赖
RUN pip install -r requirements.txt

# 安装Playwright浏览器
RUN playwright install chromium

# 构建应用
RUN python3 build_cross_platform.py

# 输出构建结果
CMD ["ls", "-la", "dist/"]
