from dataclasses import dataclass
from typing import Optional
from .enums import ConsumerType


@dataclass
class ConsumerConfig:
    """消费者配置"""
    group_id: Optional[str] = None
    consumer_type: ConsumerType = ConsumerType.SINGLE
    concurrency: int = 1
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = False
    max_poll_records: int = 500