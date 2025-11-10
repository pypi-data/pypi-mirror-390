import asyncio
import uuid
import json
import random
from logger import BaseLogger
from typing import List, Optional, Any, Dict, Tuple
from decorators.singleton import singleton
from aiokafka import AIOKafkaProducer
from dataclasses import dataclass, field
from admin.config import KafkaConfig
from .config import ProducerConfig
from .enums import ProducerStatus


@dataclass
class TopicProducer:
    """Topic 生产者实例"""

    producer_id: str
    topic: str
    producer: Optional[AIOKafkaProducer] = None
    status: ProducerStatus = ProducerStatus.NOT_STARTED
    config: ProducerConfig = field(default_factory=ProducerConfig)


@singleton
class AIOKafkaProducerManager:

    def __init__(self):
        self.config = KafkaConfig()
        self._topic_producers = {}
        # self._producer_instances = {}
        self.logger = BaseLogger(name=__name__)

    """Kafka 生产者管理器"""

    def register(self, topic: str, config: ProducerConfig) -> str:
        """注册生产者并返回 producer_id"""
        producer_id = f"producer_{topic}_{uuid.uuid4().hex[:8]}"

        if config is None:
            config = ProducerConfig()

        topic_producer = TopicProducer(
            producer_id=producer_id, topic=topic, config=config
        )

        if topic not in self._topic_producers:
            self._topic_producers[topic] = topic_producer

        return producer_id

    async def start(self, topic: str):
        """启动指定生产者"""
        if not self._topic_producers.__contains__(topic):
            raise ValueError(f"没有找到对应topic的生产者")

        topic_producer: TopicProducer = self._topic_producers[topic]

        if topic_producer.producer is not None:
            return

        if (
            topic_producer.status == ProducerStatus.RUNNING
            or topic_producer.status == ProducerStatus.STARTING
        ):
            return

        # if not self._service_started:
        #     await self.start_service()
        try:
            topic_producer.status = ProducerStatus.STARTING
            producer_config = {
                "bootstrap_servers": self.config.kafka_bootstrap_servers,
                "value_serializer": lambda v: json.dumps(v).encode("utf-8"),
                "acks": topic_producer.config.acks,
                "max_batch_size": topic_producer.config.batch_size,
                "linger_ms": topic_producer.config.linger_ms,
                "compression_type": topic_producer.config.compression_type,
                **self.config.security_config,
            }
            topic_producer.producer = AIOKafkaProducer(**producer_config)
            await topic_producer.producer.start()
            topic_producer.status = ProducerStatus.RUNNING
        except Exception as e:
            topic_producer.status = ProducerStatus.NOT_STARTED
            self.logger.error(
                f"Failed to start producer {topic_producer.producer_id}: {e}"
            )
            return

    async def send_message(self, topic: str, message: Dict[str, Any], key: str = ""):
        """使用指定生产者发送消息"""
        if not self._topic_producers.__contains__(topic):
            self.register(topic, ProducerConfig())

        topic_producer = self._topic_producers[topic]

        if topic_producer.producer is None:
            await self.start(topic)

        if topic_producer.status != ProducerStatus.RUNNING:
            await self.start(topic)

        producer: AIOKafkaProducer = topic_producer.producer

        try:
            if key:
                await producer.send_and_wait(topic, value=message, key=key.encode())
            else:
                await producer.send_and_wait(topic, value=message)

            self.logger.debug(
                f"Message sent via producer {topic_producer.producer_id} to {topic}"
            )

        except Exception as e:
            self.logger.error(
                f"Failed to send message via producer {topic_producer.producer_id}: {e}"
            )

    async def send_messages(
        self,
        topic: str,
        messages: List[dict],
        key: str,
        headers: List[Tuple[str, bytes]],
    ):
        """使用指定生产者批量发送消息"""
        if not self._topic_producers.__contains__(topic):
            self.register(topic, ProducerConfig())

        topic_producer = self._topic_producers[topic]

        if topic_producer.producer is None:
            await self.start(topic)

        producer: AIOKafkaProducer = topic_producer.producer
        try:
            batch = producer.create_batch()
            for message in messages:
                batch.append(key=key.encode(), headers=headers, value=message, timestamp=None)
            partitions = await producer.partitions_for(topic=topic)
            partition = random.choice(tuple(partitions))
            await producer.send_batch(
                batch=batch,
                topic=topic,
                partition=partition,
            )

        except Exception as e:
            self.logger.error(
                f"Failed to send messages via producer {topic_producer.producer_id}: {e}"
            )

    async def stop(self, topic: str):
        """停止指定生产者"""
        if not self._topic_producers.__contains__(topic):
            raise ValueError(f"没有找到对应topic的生产者")

        topic_producer: TopicProducer = self._topic_producers[topic]

        if (
            topic_producer.producer is None
            or topic_producer.status == ProducerStatus.STOPPED
        ):
            return

        await topic_producer.producer.stop()
        topic_producer.producer = None
        topic_producer.status = ProducerStatus.STOPPED

    async def stop_all(self) -> None:
        """停止所有生产者"""
        await asyncio.gather(
            *[self.stop(topic) for topic in self._topic_producers.keys()]
        )