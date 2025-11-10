import asyncio
from admin.manager import Akam
from consumer.manager import AIOKafkaConsumerManager
from producer.manager import AIOKafkaProducerManager


class AIOKafkaManager:

    def __init__(self) -> None:
        self.consumer_manager = AIOKafkaConsumerManager()
        self.producer_manager = AIOKafkaProducerManager()
        self.admin_manager = Akam()

    async def startup(self):
        await self.admin_manager.start()
        await self._startup_consumer()

    async def _startup_consumer(self):
        topic_consumers = self.consumer_manager.scan(None)
        for topic_consumer in topic_consumers:
            await self.admin_manager.ensure_topic_exists(topic_consumer.topic, 3, 3)
        await self.consumer_manager.start_all()

    async def shutdown(self):
        await asyncio.gather(
            self.consumer_manager.stop_all(),
            self.producer_manager.stop_all()
        )
