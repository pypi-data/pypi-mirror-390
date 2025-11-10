from typing import Callable, Optional
from functools import wraps
from .enums import ConsumerType
from .config import ConsumerConfig

def kafka_consumer(
    topic: str,
    group_id: Optional[str] = None,
    consumer_type: ConsumerType = ConsumerType.SINGLE,
    concurrency: int = 1,
    auto_offset_reset: str = "earliest",
    enable_auto_commit: bool = False,
    max_poll_records: int = 500,
):
    """
    Kafka 消费者装饰器

    Args:
        topic: Kafka topic 名称
        group_id: 消费者组 ID
        consumer_type: 消费者类型
        concurrency: 并发数
        auto_start: 是否自动启动
        auto_offset_reset: 偏移量重置策略
        enable_auto_commit: 是否自动提交
        max_poll_records: 最大拉取记录数
    """

    def decorator(func: Callable) -> Callable:
        # 创建消费者配置
        config = ConsumerConfig(
            group_id=group_id,
            consumer_type=consumer_type,
            concurrency=concurrency,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=enable_auto_commit,
            max_poll_records=max_poll_records,
        )

        setattr(func, "_is_kafka_consumer", True)
        setattr(func, "_kafka_consumer_config", config)
        setattr(func, "_topic", topic)
        
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper

    return decorator
