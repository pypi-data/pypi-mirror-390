import ssl
from pathlib import Path
from pydantic import Field
from decorators.singleton import singleton
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, Dict, Any

@singleton
class KafkaConfig(BaseSettings):
    
    kafka_bootstrap_servers: str = Field(
        default="localhost:9092",
        description="Kafka 服务器地址"
    )
    kafka_security_protocol: str = Field(
        default="PLAINTEXT",
        description="安全协议: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL"
    )
    kafka_sasl_mechanism: str = Field(
        default="PLAIN",
        description="SASL 机制: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512"
    )
    kafka_sasl_username: Optional[str] = Field(
        default=None,
        description="SASL 用户名"
    )
    kafka_sasl_password: Optional[str] = Field(
        default=None,
        description="SASL 密码"
    )
    kafka_ssl_cafile: Optional[str] = Field(
        default=None,
        description="CA 证书文件路径 (PEM 格式)"
    )
    kafka_ssl_certfile: Optional[str] = Field(
        default=None,
        description="客户端证书文件路径 (PEM 格式)"
    )
    kafka_ssl_keyfile: Optional[str] = Field(
        default=None,
        description="客户端密钥文件路径 (PEM 格式)"
    )


    # 安全配置 - 支持 JKS 格式
    kafka_ssl_keystore_location: Optional[str] = Field(
        default=None,
        description="密钥库文件路径 (JKS 格式)"
    )
    kafka_ssl_keystore_password: Optional[str] = Field(
        default=None,
        description="密钥库密码"
    )
    kafka_ssl_key_password: Optional[str] = Field(
        default=None,
        description="密钥密码"
    )
    kafka_ssl_truststore_location: Optional[str] = Field(
        default=None,
        description="信任库文件路径 (JKS 格式)"
    )
    kafka_ssl_truststore_password: Optional[str] = Field(
        default=None,
        description="信任库密码"
    )

    # 是否检查 SSL 主机名
    kafka_ssl_check_hostname: bool = Field(
        default=False,
        description="是否检查 SSL 主机名"
    )

    security_config: Dict[str, Any] = {}

    # 内部字段，不暴露给用户
    _env_file: Optional[str] = None
    
    model_config = SettingsConfigDict(
        env_prefix="KAFKA_",
        case_sensitive=False,
        extra="ignore",
        env_file=None,  # 禁用 pydantic 的自动 .env 加载，我们自己处理
    )
    
    def _auto_discover_env_file(self) -> Optional[str]:
        """
        自动发现 .kafka.env 文件
        搜索策略：
        1. 当前工作目录（Starlette 项目根目录）
        2. 向上搜索父目录（最多 3 层）
        3. 用户主目录
        """
        search_locations = []
        
        # 1. 当前工作目录（通常是 Starlette 项目根目录）
        current_dir = Path.cwd()
        search_locations.append(current_dir / ".kafka.env")
        
        # 2. 向上搜索父目录（解决子目录调用的情况）
        parent_dirs = [
            current_dir.parent,
            current_dir.parent.parent,
            current_dir.parent.parent.parent,
        ]
        for parent_dir in parent_dirs:
            if parent_dir != current_dir and parent_dir.exists():
                search_locations.append(parent_dir / ".kafka.env")
        
        # 3. 用户主目录的配置
        home_dir = Path.home()
        search_locations.extend([
            home_dir / ".kafka.env",
            home_dir / ".config" / "kafka.env",
        ])
        
        # 检查每个可能的位置
        for location in search_locations:
            print(f"Checking env file: {location}")
            if location.exists():
                return str(location)
        
        return None

    def __init__(self, **kwargs):
        # 先尝试自动发现 .kafka.env 文件
        env_file = self._auto_discover_env_file()
        
        init_kwargs = kwargs.copy()
        
        if env_file:
            # 使用发现的 env 文件
            init_kwargs['_env_file'] = env_file
            self._env_file = env_file
        
        super().__init__(**init_kwargs)
        self._setup_security_config()

    def _setup_security_config(self):
        """设置安全配置"""
        protocol = self.kafka_security_protocol.upper()
        self.security_config["security_protocol"] = protocol
        
        # 处理 SSL 相关配置
        if protocol in ["SSL", "SASL_SSL"]:
            self._setup_ssl_config()
        
        # 处理 SASL 相关配置
        if protocol in ["SASL_PLAINTEXT", "SASL_SSL"]:
            self._setup_sasl_config()

    def _setup_ssl_config(self):
        """设置 SSL 配置"""
        ssl_context = None
        
        # 优先使用 PEM 证书
        if (self.kafka_ssl_cafile and 
            self.kafka_ssl_certfile and 
            self.kafka_ssl_keyfile):
            
            ssl_context = ssl.create_default_context()
            ssl_context.load_verify_locations(self.kafka_ssl_cafile)
            ssl_context.load_cert_chain(
                certfile=self.kafka_ssl_certfile,
                keyfile=self.kafka_ssl_keyfile
            )
            ssl_context.check_hostname = self.kafka_ssl_check_hostname
        
        # 其次使用 JKS
        elif (self.kafka_ssl_keystore_location and
            self.kafka_ssl_keystore_password and
            self.kafka_ssl_truststore_location and
            self.kafka_ssl_truststore_password):
            
            self.security_config.update({
                "ssl_keystore_location": self.kafka_ssl_keystore_location,
                "ssl_keystore_password": self.kafka_ssl_keystore_password,
                "ssl_truststore_location": self.kafka_ssl_truststore_location,
                "ssl_truststore_password": self.kafka_ssl_truststore_password,
            })
        
        # 如果没有提供证书但使用纯 SSL，创建默认上下文
        elif self.kafka_security_protocol.upper() == "SSL":
            ssl_context = ssl.create_default_context()
            if not self.kafka_ssl_check_hostname:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
        
        # 设置 SSL 上下文
        if ssl_context:
            self.security_config["ssl_context"] = ssl_context

    def _setup_sasl_config(self):
        """设置 SASL 配置"""
        if self.kafka_sasl_username and self.kafka_sasl_password:
            self.security_config.update({
                "sasl_mechanism": self.kafka_sasl_mechanism.upper(),
                "sasl_plain_username": self.kafka_sasl_username,
                "sasl_plain_password": self.kafka_sasl_password,
            })