# 快速启动指南

## 前置要求

1. Python 3.12+
2. Redis 服务器
3. 已安装项目依赖

## 快速开始

### 1. 安装依赖

```bash
pip install -e .
```

### 2. 启动 Redis

确保 Redis 服务正在运行：

```bash
# Windows (如果已安装)
redis-server

# Linux/Mac
redis-server

# 或使用 Docker
docker run -d -p 6379:6379 redis:latest
```

### 3. 生成 gRPC 代码

```bash
python scripts/generate_grpc.py
```

这将在 `client/` 目录下生成 `queue_service_pb2.py` 和 `queue_service_pb2_grpc.py` 文件。

### 4. 启动 gRPC 服务器

```bash
python scripts/start_server.py
```

服务器将在 `0.0.0.0:50051` 上启动。

### 5. (可选) 启动 Celery Worker

如果需要异步处理任务，在另一个终端启动：

```bash
celery -A server.celery.app worker --loglevel=info
```

### 6. 测试客户端

在另一个终端运行：

```bash
python examples/client_example.py
```

## 环境变量配置

可以通过环境变量自定义配置：

```bash
# Redis 配置
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=your_password  # 可选

# gRPC 配置
export GRPC_HOST=0.0.0.0
export GRPC_PORT=50051

# 日志级别
export LOG_LEVEL=INFO
```

## 常见问题

### 问题：gRPC 代码生成失败

**解决方案**：确保已安装 `grpcio-tools`：

```bash
pip install grpcio-tools
```

### 问题：无法连接到 Redis

**解决方案**：
1. 检查 Redis 是否正在运行：`redis-cli ping`（应该返回 `PONG`）
2. 检查环境变量配置是否正确
3. 检查防火墙设置

### 问题：导入错误

**解决方案**：
1. 确保已生成 gRPC 代码：`python scripts/generate_grpc.py`
2. 确保已安装所有依赖：`pip install -e .`
3. 检查 Python 路径是否正确

## 下一步

- 查看 [README.md](README.md) 了解完整的 API 文档
- 查看 `examples/client_example.py` 了解如何使用客户端
- 查看 `tests/` 目录了解如何编写测试

