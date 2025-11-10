import ssl
from logger import BaseLogger
from decorators.singleton import singleton
from typing import Optional
from admin.config import KafkaConfig
from aiokafka.admin import AIOKafkaAdminClient, NewTopic


@singleton
class Akam:
    

    def __init__(self):
        self.admin_client: Optional[AIOKafkaAdminClient] = None
        self.config = KafkaConfig()
        self._service_started = False
        self.logger = BaseLogger(name=__name__)


    
    async def start(self) -> None:
        """启动 Kafka 服务"""
        if self._service_started:
            self.logger.warning("Kafka service already started")
            return
        config = KafkaConfig()
        try:
            self.admin_client = AIOKafkaAdminClient(
                bootstrap_servers=config.kafka_bootstrap_servers,
                **self.config.security_config
            )
            await self.admin_client.start()
            self._service_started = True
            self.logger.info("Kafka admin client started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start Kafka admin client: {e}")
            raise

    async def ensure_topic_exists(self, topic: str, num_partitions: int = 1, replication_factor: int = 1):
        """确保 topic 存在"""
        if not self._service_started:
            await self.start()
            
        try:
            # 检查 topic 是否已存在
            assert self.admin_client
            topics = await self.admin_client.describe_topics([topic])
            if topic not in topics:
                new_topic = NewTopic(
                    name=topic,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                )
                await self.admin_client.create_topics([new_topic])
                self.logger.debug(f"Created topic: {topic}")
                
        except Exception as e:
            self.logger.warning(f"check/create Topic 失败 {topic}: {e}")

    

