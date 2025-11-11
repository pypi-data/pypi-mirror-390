"""私有化 Agent 任务队列客户端模块"""
# 导出客户端类
try:
    from .agent_queue import PrivateAgentTasksQueue, AgentClient, create_client, AgentQueue
    from .agent_queue_manager import AgentQueueManager, create_manager
    from .agent_queue_report import (
        AgentQueueReportClient,
        AgentQueueReport,
        QueueReport,
        create_report_client
    )
    __all__ = [
        "PrivateAgentTasksQueue",
        "AgentClient",
        "create_client",
        "AgentQueue",
        "AgentQueueManager",
        "create_manager",
        "AgentQueueReportClient",
        "AgentQueueReport",
        "QueueReport",
        "create_report_client"
    ]
except ImportError:
    __all__ = []

