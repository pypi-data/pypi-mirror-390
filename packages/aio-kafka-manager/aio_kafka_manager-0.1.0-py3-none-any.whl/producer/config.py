from dataclasses import dataclass
from .enums import ProducerType

@dataclass
class ProducerConfig:
    """生产者配置"""
    producer_type: ProducerType = ProducerType.DEFAULT
    acks: str = "all"
    batch_size: int = 16384
    linger_ms: int = 0
    compression_type: str = "gzip"