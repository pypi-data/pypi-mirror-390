"""Agent 客户端接口 - 优化的 gRPC 接口封装"""
# gRPC 生成的代码会在这里
# 需要运行: python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I. client/queue_service.proto

# 导出 gRPC 生成的代码（生成后可用）
try:
    from client import queue_service_pb2, queue_service_pb2_grpc
    
    # ========== 服务类 ==========
    QueueServiceStub = queue_service_pb2_grpc.QueueServiceStub
    
    # ========== 消息类型 ==========
    # 请求消息
    CreateQueueRequest = queue_service_pb2.CreateQueueRequest
    QueueExistsRequest = queue_service_pb2.QueueExistsRequest
    GetQueueInfoRequest = queue_service_pb2.GetQueueInfoRequest
    ClearQueueRequest = queue_service_pb2.ClearQueueRequest
    SubmitTaskRequest = queue_service_pb2.SubmitTaskRequest
    BatchSubmitTasksRequest = queue_service_pb2.BatchSubmitTasksRequest
    SubmitTaskItem = queue_service_pb2.SubmitTaskItem
    GetTaskRequest = queue_service_pb2.GetTaskRequest
    QueryTaskRequest = queue_service_pb2.QueryTaskRequest
    UpdateTaskStatusRequest = queue_service_pb2.UpdateTaskStatusRequest
    DeleteTaskRequest = queue_service_pb2.DeleteTaskRequest
    BatchDeleteTasksRequest = queue_service_pb2.BatchDeleteTasksRequest
    CancelTaskRequest = queue_service_pb2.CancelTaskRequest
    RetryTaskRequest = queue_service_pb2.RetryTaskRequest
    ListTasksRequest = queue_service_pb2.ListTasksRequest
    GetTaskStatsRequest = queue_service_pb2.GetTaskStatsRequest
    HealthCheckRequest = queue_service_pb2.HealthCheckRequest
    
    # 响应消息
    CreateQueueResponse = queue_service_pb2.CreateQueueResponse
    QueueExistsResponse = queue_service_pb2.QueueExistsResponse
    GetQueueInfoResponse = queue_service_pb2.GetQueueInfoResponse
    ClearQueueResponse = queue_service_pb2.ClearQueueResponse
    SubmitTaskResponse = queue_service_pb2.SubmitTaskResponse
    BatchSubmitTasksResponse = queue_service_pb2.BatchSubmitTasksResponse
    GetTaskResponse = queue_service_pb2.GetTaskResponse
    QueryTaskResponse = queue_service_pb2.QueryTaskResponse
    UpdateTaskStatusResponse = queue_service_pb2.UpdateTaskStatusResponse
    DeleteTaskResponse = queue_service_pb2.DeleteTaskResponse
    BatchDeleteTasksResponse = queue_service_pb2.BatchDeleteTasksResponse
    CancelTaskResponse = queue_service_pb2.CancelTaskResponse
    RetryTaskResponse = queue_service_pb2.RetryTaskResponse
    ListTasksResponse = queue_service_pb2.ListTasksResponse
    GetTaskStatsResponse = queue_service_pb2.GetTaskStatsResponse
    HealthCheckResponse = queue_service_pb2.HealthCheckResponse
    
    # 数据模型
    Task = queue_service_pb2.Task
    
    # ========== 枚举类型 ==========
    TaskStatus = queue_service_pb2.TaskStatus
    TaskType = queue_service_pb2.TaskType
    
    # ========== 枚举值（方便使用） ==========
    # TaskStatus 枚举值
    PENDING = TaskStatus.PENDING
    PROCESSING = TaskStatus.PROCESSING
    COMPLETED = TaskStatus.COMPLETED
    FAILED = TaskStatus.FAILED
    
    # TaskType 枚举值
    UNKNOWN = TaskType.UNKNOWN
    DATA_PROCESSING = TaskType.DATA_PROCESSING
    IMAGE_PROCESSING = TaskType.IMAGE_PROCESSING
    TEXT_ANALYSIS = TaskType.TEXT_ANALYSIS
    MODEL_INFERENCE = TaskType.MODEL_INFERENCE
    DATA_EXTRACTION = TaskType.DATA_EXTRACTION
    FILE_UPLOAD = TaskType.FILE_UPLOAD
    FILE_DOWNLOAD = TaskType.FILE_DOWNLOAD
    API_CALL = TaskType.API_CALL
    DATABASE_QUERY = TaskType.DATABASE_QUERY
    CUSTOM = TaskType.CUSTOM
    
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
    ]
except ImportError:
    # gRPC 代码还未生成
    __all__ = []

# 导出配置模块
try:
    from client.config import settings, ClientSettings
    __all__.extend(["settings", "ClientSettings"])
except ImportError:
    pass

# 导出客户端工厂
try:
    from client.client import AgentClient, create_client
    __all__.extend(["AgentClient", "create_client"])
except ImportError:
    pass