# gRPC 重试和自动重连机制

## 概述

本模块实现了 gRPC 客户端的自动重试和自动重连机制，提高了系统的可靠性和容错能力。

## 功能特性

### 1. 自动重试机制

- **指数退避策略**：重试间隔按指数增长，避免对服务器造成过大压力
- **可配置重试次数**：通过 `max_retry_attempts` 配置最大重试次数
- **智能状态码判断**：只对可重试的状态码进行重试（如 UNAVAILABLE、DEADLINE_EXCEEDED 等）
- **详细日志记录**：记录每次重试的详细信息，便于问题排查

### 2. 自动重连机制

- **Keepalive 检测**：通过 keepalive ping 定期检测连接状态
- **自动重连**：连接断开时自动尝试重连
- **连接稳定性优化**：配置 HTTP/2 ping 参数，增强连接稳定性

## 配置说明

### 重试配置

在 `client/config/grpc.yaml` 中配置：

```yaml
grpc:
  # 重试配置
  max_retry_attempts: 3              # 最大重试次数（0 表示禁用重试）
  initial_backoff: 1.0               # 初始退避时间（秒）
  max_backoff: 10.0                  # 最大退避时间（秒）
  backoff_multiplier: 2.0            # 退避倍数
  retryable_status_codes:            # 可重试的状态码
    - UNAVAILABLE
    - DEADLINE_EXCEEDED
    - RESOURCE_EXHAUSTED
    - ABORTED
    - INTERNAL
    - UNKNOWN
```

### 自动重连配置

```yaml
grpc:
  # 连接配置
  keepalive_time: 30                 # Keepalive 时间（秒）
  keepalive_timeout: 5               # Keepalive 超时（秒）
  keepalive_permit_without_calls: true  # 允许在没有调用时发送 keepalive
```

## 使用示例

### 基本使用

```python
from client.queues.agent_queue import PrivateAgentTasksQueue

# 使用默认配置（自动启用重试和重连）
queue = PrivateAgentTasksQueue()

# 调用会自动重试失败的请求
response = queue.create_queue("agent_001")
```

### 自定义重试配置

```python
# 自定义重试次数和退避策略
queue = PrivateAgentTasksQueue(
    grpc_max_retry_attempts=5,      # 最多重试 5 次
    grpc_initial_backoff=2.0,        # 初始退避 2 秒
    grpc_max_backoff=20.0,           # 最大退避 20 秒
    grpc_backoff_multiplier=1.5      # 退避倍数 1.5
)
```

### 禁用重试

```python
# 禁用自动重试
queue = PrivateAgentTasksQueue(grpc_max_retry_attempts=0)
```

## 工作原理

### 重试机制

1. 当 gRPC 调用失败时，拦截器会检查错误状态码
2. 如果状态码在可重试列表中，且未达到最大重试次数，则进行重试
3. 重试前会等待一段时间（指数退避），避免频繁重试
4. 重试间隔计算：`min(initial_backoff * (multiplier ^ attempt), max_backoff)`

### 自动重连机制

1. gRPC 通道通过 keepalive ping 定期检测连接状态
2. 如果 keepalive 超时，通道会自动尝试重连
3. 重连使用指数退避策略（由 gRPC 底层实现）
4. 重连成功后，后续调用会自动使用新连接

## 注意事项

1. **流式调用不重试**：重试机制只对一元一元调用生效，流式调用不进行重试
2. **幂等性要求**：确保你的操作是幂等的，因为重试可能导致操作被执行多次
3. **超时设置**：合理设置超时时间，避免重试导致的总耗时过长
4. **日志监控**：关注重试日志，频繁重试可能表示服务器存在问题

## 性能影响

- **延迟增加**：重试会增加请求的总延迟，但提高了成功率
- **服务器负载**：指数退避策略可以减轻对服务器的压力
- **连接开销**：自动重连会消耗一定的网络资源，但保证了连接的可用性

