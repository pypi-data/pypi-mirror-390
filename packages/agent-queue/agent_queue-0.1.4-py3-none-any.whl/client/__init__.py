"""Agent 客户端接口 - 优化的 gRPC 接口封装"""
# 从 service 包重新导出所有类型，保持向后兼容

# 导出 gRPC 生成的代码和客户端（从 service 包）
try:
    from client.service import (
        # 原始模块
        queue_service_pb2,
        queue_service_pb2_grpc,
        # 服务类
        QueueServiceStub,
        # 请求消息
        CreateQueueRequest,
        QueueExistsRequest,
        GetQueueInfoRequest,
        ClearQueueRequest,
        SubmitTaskRequest,
        BatchSubmitTasksRequest,
        SubmitTaskItem,
        GetTaskRequest,
        QueryTaskRequest,
        UpdateTaskStatusRequest,
        DeleteTaskRequest,
        BatchDeleteTasksRequest,
        CancelTaskRequest,
        RetryTaskRequest,
        ListTasksRequest,
        GetTaskStatsRequest,
        HealthCheckRequest,
        # 响应消息
        CreateQueueResponse,
        QueueExistsResponse,
        GetQueueInfoResponse,
        ClearQueueResponse,
        SubmitTaskResponse,
        BatchSubmitTasksResponse,
        GetTaskResponse,
        QueryTaskResponse,
        UpdateTaskStatusResponse,
        DeleteTaskResponse,
        BatchDeleteTasksResponse,
        CancelTaskResponse,
        RetryTaskResponse,
        ListTasksResponse,
        GetTaskStatsResponse,
        HealthCheckResponse,
        # 数据模型
        Task,
        # 枚举类型
        TaskStatus,
        TaskType,
        # 枚举值
        PENDING,
        PROCESSING,
        COMPLETED,
        FAILED,
        UNKNOWN,
        DATA_PROCESSING,
        IMAGE_PROCESSING,
        TEXT_ANALYSIS,
        MODEL_INFERENCE,
        DATA_EXTRACTION,
        FILE_UPLOAD,
        FILE_DOWNLOAD,
        API_CALL,
        DATABASE_QUERY,
        CUSTOM,
    )
    
    # 从 queues 包导入客户端类
    from client.queues import (
        PrivateAgentTasksQueue,
        AgentClient,  # 向后兼容别名
        create_client,
    )
    
    __all__ = [
        # 服务类
        "QueueServiceStub",
        # 请求消息
        "CreateQueueRequest",
        "QueueExistsRequest",
        "GetQueueInfoRequest",
        "ClearQueueRequest",
        "SubmitTaskRequest",
        "BatchSubmitTasksRequest",
        "SubmitTaskItem",
        "GetTaskRequest",
        "QueryTaskRequest",
        "UpdateTaskStatusRequest",
        "DeleteTaskRequest",
        "BatchDeleteTasksRequest",
        "CancelTaskRequest",
        "RetryTaskRequest",
        "ListTasksRequest",
        "GetTaskStatsRequest",
        "HealthCheckRequest",
        # 响应消息
        "CreateQueueResponse",
        "QueueExistsResponse",
        "GetQueueInfoResponse",
        "ClearQueueResponse",
        "SubmitTaskResponse",
        "BatchSubmitTasksResponse",
        "GetTaskResponse",
        "QueryTaskResponse",
        "UpdateTaskStatusResponse",
        "DeleteTaskResponse",
        "BatchDeleteTasksResponse",
        "CancelTaskResponse",
        "RetryTaskResponse",
        "ListTasksResponse",
        "GetTaskStatsResponse",
        "HealthCheckResponse",
        # 数据模型
        "Task",
        # 枚举类型
        "TaskStatus",
        "TaskType",
        # 枚举值
        "PENDING",
        "PROCESSING",
        "COMPLETED",
        "FAILED",
        "UNKNOWN",
        "DATA_PROCESSING",
        "IMAGE_PROCESSING",
        "TEXT_ANALYSIS",
        "MODEL_INFERENCE",
        "DATA_EXTRACTION",
        "FILE_UPLOAD",
        "FILE_DOWNLOAD",
        "API_CALL",
        "DATABASE_QUERY",
        "CUSTOM",
        # 原始模块（向后兼容）
        "queue_service_pb2",
        "queue_service_pb2_grpc",
        # 客户端类
        "PrivateAgentTasksQueue",
        "AgentClient",  # 向后兼容别名
        "create_client",
    ]
except ImportError:
    # gRPC 代码还未生成或 service 包不可用
    __all__ = []

# 导出配置模块
try:
    from client.config import settings, ClientSettings
    __all__.extend(["settings", "ClientSettings"])
except ImportError:
    pass
