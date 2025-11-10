"""客户端配置 - 从 YAML 文件加载配置，支持环境变量覆盖"""
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml


class ClientSettings:
    """客户端配置类 - 支持配置继承和覆盖"""
    
    def __init__(self, config_path: Optional[str] = None, base_settings: Optional['ClientSettings'] = None, **overrides):
        """
        初始化客户端配置
        
        Args:
            config_path: 配置文件路径（可选）
                        - 如果为 None，则从环境变量 GRPC_CONFIG_PATH 读取
                        - 如果环境变量也未设置，则使用默认路径 client/config/grpc.yaml
            base_settings: 基础配置实例（可选），用于配置继承
            **overrides: 配置覆盖项，可以直接传入配置值覆盖默认值
                        例如: ClientSettings(GRPC_HOST="192.168.1.100", GRPC_PORT=50052)
        """
        # 如果有基础配置，先继承
        if base_settings is not None:
            self._copy_from(base_settings)
        else:
            # 确定配置文件路径
            if config_path is None:
                config_path = os.getenv("GRPC_CONFIG_PATH")
            
            if config_path is None:
                # 使用默认路径
                config_dir = Path(__file__).parent
                config_path = config_dir / "grpc.yaml"
            else:
                config_path = Path(config_path)
            
            # 加载配置
            self._load_grpc_config(config_path)
        
        # 应用覆盖项
        for key, value in overrides.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def _copy_from(self, other: 'ClientSettings'):
        """从另一个配置实例复制所有属性"""
        for attr in dir(other):
            if not attr.startswith('_') and not callable(getattr(other, attr)):
                # 跳过 property 属性（只读属性）
                if isinstance(getattr(type(other), attr, None), property):
                    continue
                try:
                    setattr(self, attr, getattr(other, attr))
                except AttributeError:
                    # 如果属性是只读的，跳过
                    pass
    
    def copy(self, **overrides) -> 'ClientSettings':
        """
        创建配置副本，并应用覆盖项
        
        Args:
            **overrides: 要覆盖的配置项
            
        Returns:
            新的配置实例
        """
        new_settings = ClientSettings(base_settings=self, **overrides)
        return new_settings
    
    def _load_grpc_config(self, config_path: Path):
        """加载 gRPC 配置"""
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                grpc_config = config.get("grpc", {})
                
                # 服务器连接配置（优先使用环境变量）
                self.GRPC_HOST: str = os.getenv("GRPC_HOST", grpc_config.get("host", "localhost"))
                self.GRPC_PORT: int = int(os.getenv("GRPC_PORT", str(grpc_config.get("port", 50051))))
                
                # 连接配置
                self.GRPC_TIMEOUT: float = float(os.getenv("GRPC_TIMEOUT", str(grpc_config.get("timeout", 30))))
                self.GRPC_KEEPALIVE_TIME: int = int(grpc_config.get("keepalive_time", 30))
                self.GRPC_KEEPALIVE_TIMEOUT: int = int(grpc_config.get("keepalive_timeout", 5))
                self.GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS: bool = grpc_config.get("keepalive_permit_without_calls", True)
                
                # 重试配置
                self.GRPC_MAX_RETRY_ATTEMPTS: int = int(grpc_config.get("max_retry_attempts", 3))
                self.GRPC_INITIAL_BACKOFF: float = float(grpc_config.get("initial_backoff", 1.0))
                self.GRPC_MAX_BACKOFF: float = float(grpc_config.get("max_backoff", 10.0))
                self.GRPC_BACKOFF_MULTIPLIER: float = float(grpc_config.get("backoff_multiplier", 2.0))
                self.GRPC_RETRYABLE_STATUS_CODES: List[str] = grpc_config.get("retryable_status_codes", [
                    "UNAVAILABLE",
                    "DEADLINE_EXCEEDED",
                    "RESOURCE_EXHAUSTED",
                    "ABORTED",
                    "INTERNAL",
                    "UNKNOWN"
                ])
                
                # 连接池配置
                self.GRPC_MAX_RECEIVE_MESSAGE_LENGTH: int = int(grpc_config.get("max_receive_message_length", 4194304))
                self.GRPC_MAX_SEND_MESSAGE_LENGTH: int = int(grpc_config.get("max_send_message_length", 4194304))
                
                # SSL/TLS 配置
                self.GRPC_USE_TLS: bool = grpc_config.get("use_tls", False)
                self.GRPC_TLS_CA_CERTS: Optional[str] = grpc_config.get("tls_ca_certs")
                self.GRPC_TLS_CLIENT_CERT: Optional[str] = grpc_config.get("tls_client_cert")
                self.GRPC_TLS_CLIENT_KEY: Optional[str] = grpc_config.get("tls_client_key")
                self.GRPC_TLS_SERVER_HOSTNAME_OVERRIDE: Optional[str] = grpc_config.get("tls_server_hostname_override")
                
                # 压缩配置
                self.GRPC_COMPRESSION: Optional[str] = grpc_config.get("compression")
                
                # 等待就绪配置
                self.GRPC_WAIT_FOR_READY: bool = grpc_config.get("wait_for_ready", False)
                self.GRPC_WAIT_FOR_READY_TIMEOUT: int = int(grpc_config.get("wait_for_ready_timeout", 5))
                
                # 拦截器配置
                self.GRPC_INTERCEPTORS: List[str] = grpc_config.get("interceptors", [])
                
                # 日志配置
                self.GRPC_ENABLE_LOGGING: bool = grpc_config.get("enable_logging", False)
                self.GRPC_LOG_LEVEL: str = grpc_config.get("log_level", "INFO")
        else:
            # 如果配置文件不存在，使用环境变量或默认值
            self.GRPC_HOST: str = os.getenv("GRPC_HOST", "localhost")
            self.GRPC_PORT: int = int(os.getenv("GRPC_PORT", "50051"))
            self.GRPC_TIMEOUT: float = float(os.getenv("GRPC_TIMEOUT", "30"))
            self.GRPC_KEEPALIVE_TIME: int = 30
            self.GRPC_KEEPALIVE_TIMEOUT: int = 5
            self.GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS: bool = True
            self.GRPC_MAX_RETRY_ATTEMPTS: int = 3
            self.GRPC_INITIAL_BACKOFF: float = 1.0
            self.GRPC_MAX_BACKOFF: float = 10.0
            self.GRPC_BACKOFF_MULTIPLIER: float = 2.0
            self.GRPC_RETRYABLE_STATUS_CODES: List[str] = [
                "UNAVAILABLE",
                "DEADLINE_EXCEEDED",
                "RESOURCE_EXHAUSTED",
                "ABORTED",
                "INTERNAL",
                "UNKNOWN"
            ]
            self.GRPC_MAX_RECEIVE_MESSAGE_LENGTH: int = 4194304
            self.GRPC_MAX_SEND_MESSAGE_LENGTH: int = 4194304
            self.GRPC_USE_TLS: bool = False
            self.GRPC_TLS_CA_CERTS: Optional[str] = None
            self.GRPC_TLS_CLIENT_CERT: Optional[str] = None
            self.GRPC_TLS_CLIENT_KEY: Optional[str] = None
            self.GRPC_TLS_SERVER_HOSTNAME_OVERRIDE: Optional[str] = None
            self.GRPC_COMPRESSION: Optional[str] = None
            self.GRPC_WAIT_FOR_READY: bool = False
            self.GRPC_WAIT_FOR_READY_TIMEOUT: int = 5
            self.GRPC_INTERCEPTORS: List[str] = []
            self.GRPC_ENABLE_LOGGING: bool = False
            self.GRPC_LOG_LEVEL: str = "INFO"
    
    @property
    def GRPC_ADDRESS(self) -> str:
        """获取 gRPC 服务器地址（host:port 格式）"""
        return f"{self.GRPC_HOST}:{self.GRPC_PORT}"
    
    def get_channel_options(self) -> List[tuple]:
        """
        获取 gRPC 通道选项
        
        Returns:
            gRPC 通道选项列表
        """
        options = [
            ('grpc.keepalive_time_ms', self.GRPC_KEEPALIVE_TIME * 1000),
            ('grpc.keepalive_timeout_ms', self.GRPC_KEEPALIVE_TIMEOUT * 1000),
            ('grpc.keepalive_permit_without_calls', self.GRPC_KEEPALIVE_PERMIT_WITHOUT_CALLS),
            ('grpc.max_receive_message_length', self.GRPC_MAX_RECEIVE_MESSAGE_LENGTH),
            ('grpc.max_send_message_length', self.GRPC_MAX_SEND_MESSAGE_LENGTH),
        ]
        
        if self.GRPC_COMPRESSION:
            options.append(('grpc.default_compression_algorithm', self.GRPC_COMPRESSION))
        
        if self.GRPC_WAIT_FOR_READY:
            options.append(('grpc.wait_for_ready', True))
        
        return options
    
    def get_credentials(self):
        """
        获取 gRPC 凭证（如果需要 TLS）
        
        Returns:
            gRPC 凭证对象，如果不需要 TLS 则返回 None
        """
        if not self.GRPC_USE_TLS:
            return None
        
        import grpc
        
        # 加载 TLS 凭证
        if self.GRPC_TLS_CA_CERTS:
            with open(self.GRPC_TLS_CA_CERTS, 'rb') as f:
                root_certificates = f.read()
        else:
            root_certificates = None
        
        if self.GRPC_TLS_CLIENT_CERT and self.GRPC_TLS_CLIENT_KEY:
            with open(self.GRPC_TLS_CLIENT_CERT, 'rb') as f:
                certificate_chain = f.read()
            with open(self.GRPC_TLS_CLIENT_KEY, 'rb') as f:
                private_key = f.read()
        else:
            certificate_chain = None
            private_key = None
        
        # 创建凭证
        credentials = grpc.ssl_channel_credentials(
            root_certificates=root_certificates,
            private_key=private_key,
            certificate_chain=certificate_chain
        )
        
        return credentials


# 全局配置实例（使用默认配置）
_default_settings = None


def get_settings(config_path: Optional[str] = None) -> ClientSettings:
    """
    获取配置实例（单例模式）
    
    Args:
        config_path: 配置文件路径（可选）
    
    Returns:
        配置实例
    """
    global _default_settings
    
    if config_path is None and _default_settings is not None:
        return _default_settings
    
    _default_settings = ClientSettings(config_path)
    return _default_settings

