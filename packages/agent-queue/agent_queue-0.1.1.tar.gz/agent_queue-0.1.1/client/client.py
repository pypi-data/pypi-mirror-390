"""客户端工厂 - 提供便捷的客户端创建方式，支持 agent 级别的配置"""
import grpc
from typing import Optional
from client.config import ClientSettings, settings as default_settings
from client import QueueServiceStub


class AgentClient:
    """
    Agent 客户端 - 封装 gRPC 客户端，支持 agent 级别的配置
    
    使用示例:
        # 使用默认配置
        client = AgentClient()
        
        # 使用自定义配置
        client = AgentClient(
            grpc_host="192.168.1.100",
            grpc_port=50052,
            grpc_timeout=60
        )
        
        # 使用配置文件
        client = AgentClient(config_path="/path/to/config.yaml")
        
        # 基于默认配置覆盖部分配置
        client = AgentClient(
            base_settings=default_settings,
            grpc_host="192.168.1.100"
        )
        
        # 使用客户端
        response = client.create_queue("agent_001")
    """
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        base_settings: Optional[ClientSettings] = None,
        grpc_host: Optional[str] = None,
        grpc_port: Optional[int] = None,
        grpc_timeout: Optional[float] = None,
        grpc_use_tls: Optional[bool] = None,
        **grpc_config_overrides
    ):
        """
        初始化 Agent 客户端
        
        Args:
            config_path: 配置文件路径（可选）
            base_settings: 基础配置实例（可选），默认使用全局默认配置
            grpc_host: gRPC 服务器地址（可选，覆盖配置）
            grpc_port: gRPC 服务器端口（可选，覆盖配置）
            grpc_timeout: 超时时间（可选，覆盖配置）
            grpc_use_tls: 是否使用 TLS（可选，覆盖配置）
            **grpc_config_overrides: 其他 gRPC 配置覆盖项
                                    例如: grpc_keepalive_time=60, grpc_max_retry_attempts=5
        """
        # 确定基础配置
        if base_settings is None:
            base_settings = default_settings
        
        # 构建配置覆盖字典
        overrides = {}
        if grpc_host is not None:
            overrides['GRPC_HOST'] = grpc_host
        if grpc_port is not None:
            overrides['GRPC_PORT'] = grpc_port
        if grpc_timeout is not None:
            overrides['GRPC_TIMEOUT'] = grpc_timeout
        if grpc_use_tls is not None:
            overrides['GRPC_USE_TLS'] = grpc_use_tls
        
        # 处理其他配置覆盖（将 grpc_ 前缀转换为 GRPC_ 前缀）
        for key, value in grpc_config_overrides.items():
            if key.startswith('grpc_'):
                # 将 grpc_xxx 转换为 GRPC_XXX
                config_key = key.upper()
                overrides[config_key] = value
        
        # 创建配置实例
        if config_path is not None:
            # 如果指定了配置文件路径，从配置文件加载，然后应用覆盖
            self.settings = ClientSettings(config_path=config_path, **overrides)
        else:
            # 基于基础配置创建新配置，应用覆盖
            self.settings = base_settings.copy(**overrides)
        
        # 创建 gRPC 通道
        self.channel = self._create_channel()
        
        # 创建服务客户端
        self.stub = QueueServiceStub(self.channel)
    
    def _create_channel(self) -> grpc.Channel:
        """创建 gRPC 通道"""
        address = self.settings.GRPC_ADDRESS
        options = self.settings.get_channel_options()
        credentials = self.settings.get_credentials()
        
        if credentials is not None:
            # 使用安全通道
            channel = grpc.secure_channel(address, credentials, options=options)
        else:
            # 使用非安全通道
            channel = grpc.insecure_channel(address, options=options)
        
        return channel
    
    def close(self):
        """关闭客户端连接"""
        if self.channel:
            self.channel.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
    
    # ========== 队列管理接口 ==========
    
    def create_queue(self, agent_id: str):
        """创建队列"""
        from client import CreateQueueRequest
        return self.stub.CreateQueue(CreateQueueRequest(agent_id=agent_id))
    
    def queue_exists(self, agent_id: str):
        """检查队列是否存在"""
        from client import QueueExistsRequest
        return self.stub.QueueExists(QueueExistsRequest(agent_id=agent_id))
    
    def get_queue_info(self, agent_id: str):
        """获取队列信息"""
        from client import GetQueueInfoRequest
        return self.stub.GetQueueInfo(GetQueueInfoRequest(agent_id=agent_id))
    
    def clear_queue(self, agent_id: str, status: int = 0):
        """清空队列"""
        from client import ClearQueueRequest
        return self.stub.ClearQueue(ClearQueueRequest(agent_id=agent_id, status=status))
    
    # ========== 任务操作接口 ==========
    
    def submit_task(self, agent_id: str, task_type: int, payload: str, custom_task_type: str = ""):
        """提交任务"""
        from client import SubmitTaskRequest
        return self.stub.SubmitTask(SubmitTaskRequest(
            agent_id=agent_id,
            type=task_type,
            task_type=custom_task_type,
            payload=payload
        ))
    
    def batch_submit_tasks(self, agent_id: str, tasks):
        """批量提交任务"""
        from client import BatchSubmitTasksRequest
        return self.stub.BatchSubmitTasks(BatchSubmitTasksRequest(
            agent_id=agent_id,
            tasks=tasks
        ))
    
    def get_task(self, agent_id: str, timeout: int = 0):
        """获取任务"""
        from client import GetTaskRequest
        return self.stub.GetTask(GetTaskRequest(agent_id=agent_id, timeout=timeout))
    
    def query_task(self, task_id: str, agent_id: str):
        """查询任务"""
        from client import QueryTaskRequest
        return self.stub.QueryTask(QueryTaskRequest(task_id=task_id, agent_id=agent_id))
    
    def update_task_status(self, task_id: str, agent_id: str, status: int, result: str = "", error_message: str = ""):
        """更新任务状态"""
        from client import UpdateTaskStatusRequest
        return self.stub.UpdateTaskStatus(UpdateTaskStatusRequest(
            task_id=task_id,
            agent_id=agent_id,
            status=status,
            result=result,
            error_message=error_message
        ))
    
    def delete_task(self, task_id: str, agent_id: str):
        """删除任务"""
        from client import DeleteTaskRequest
        return self.stub.DeleteTask(DeleteTaskRequest(task_id=task_id, agent_id=agent_id))
    
    def batch_delete_tasks(self, agent_id: str, task_ids: list, status: int = 0):
        """批量删除任务"""
        from client import BatchDeleteTasksRequest
        return self.stub.BatchDeleteTasks(BatchDeleteTasksRequest(
            agent_id=agent_id,
            task_ids=task_ids,
            status=status
        ))
    
    def cancel_task(self, task_id: str, agent_id: str, reason: str = ""):
        """取消任务"""
        from client import CancelTaskRequest
        return self.stub.CancelTask(CancelTaskRequest(
            task_id=task_id,
            agent_id=agent_id,
            reason=reason
        ))
    
    def retry_task(self, task_id: str, agent_id: str):
        """重试任务"""
        from client import RetryTaskRequest
        return self.stub.RetryTask(RetryTaskRequest(task_id=task_id, agent_id=agent_id))
    
    # ========== 任务查询接口 ==========
    
    def list_tasks(self, agent_id: str, status: int = 0, limit: int = 100, offset: int = 0):
        """列出任务"""
        from client import ListTasksRequest
        return self.stub.ListTasks(ListTasksRequest(
            agent_id=agent_id,
            status=status,
            limit=limit,
            offset=offset
        ))
    
    def get_task_stats(self, agent_id: str, status: int = 0):
        """获取任务统计信息"""
        from client import GetTaskStatsRequest
        return self.stub.GetTaskStats(GetTaskStatsRequest(agent_id=agent_id, status=status))


def create_client(
    config_path: Optional[str] = None,
    base_settings: Optional[ClientSettings] = None,
    **config_overrides
) -> AgentClient:
    """
    便捷函数：创建 Agent 客户端
    
    Args:
        config_path: 配置文件路径（可选）
        base_settings: 基础配置实例（可选）
        **config_overrides: 配置覆盖项
        
    Returns:
        AgentClient 实例
        
    示例:
        # 使用默认配置
        client = create_client()
        
        # 覆盖部分配置
        client = create_client(grpc_host="192.168.1.100", grpc_port=50052)
        
        # 使用配置文件
        client = create_client(config_path="/path/to/config.yaml")
    """
    return AgentClient(
        config_path=config_path,
        base_settings=base_settings,
        **config_overrides
    )

