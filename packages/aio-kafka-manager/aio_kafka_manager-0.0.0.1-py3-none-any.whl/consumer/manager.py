import uuid
import inspect
from logger import BaseLogger
from dataclasses import dataclass, field
from aiokafka import AIOKafkaConsumer
from decorators.singleton import singleton
from typing import Optional, Callable, List, Dict
from admin.config import KafkaConfig
from .enums import ConsumerStatus
from .config import ConsumerConfig
import asyncio


@dataclass
class TopicConsumer:
    """Topic 消费者实例"""

    consumer_id: str
    topic: str
    handler: Callable
    consumer: Optional[AIOKafkaConsumer] = None
    tasks: List[asyncio.Task] = field(default_factory=list)
    status: ConsumerStatus = ConsumerStatus.NOT_STARTED
    config: ConsumerConfig = field(default_factory=ConsumerConfig)


@singleton
class AIOKafkaConsumerManager:
    """Kafka 消费者管理器"""

    def __init__(self):
        self.config = KafkaConfig()
        self._topic_consumer: Dict[str, TopicConsumer] = {}
        self._consumer_instances: Dict[str, TopicConsumer] = {}
        self.logger = BaseLogger(name=__name__)

    def scan(self, module=None) -> List[TopicConsumer]:
        import inspect
        import sys
        from types import ModuleType
        print("所有已加载模块:")
        for name, mod in sys.modules.items():
            if mod and hasattr(mod, "__name__"):
                print(f"  - {name}")
        modules = []
        if module is None:
            # 扫描所有已加载的模块，但过滤掉系统模块
            modules = [
                mod for mod in sys.modules.values() 
                if mod and hasattr(mod, "__name__") 
                and not mod.__name__.startswith(('_', 'builtins', 'sys', 'importlib'))
            ]
            main_module = sys.modules.get('__main__')
            # 确保主模块在列表中
            if main_module and main_module not in modules:
                modules.append(main_module)
        elif isinstance(module, ModuleType):
            modules = [module]
        elif isinstance(module, list):
            modules = module
        else:
            modules = []

        topic_consumers = []
        scanned_functions = set()  # 避免重复扫描
        

        for mod in modules:
            if not mod or not hasattr(mod, "__dict__"):
                continue
                
            mod_name = getattr(mod, "__name__", "unknown")

            # 扫描模块中的函数
            for name, obj in mod.__dict__.items():
                if name in scanned_functions:
                    continue
                    
                if inspect.isfunction(obj):
                    self._scan_function(obj, name, mod_name, topic_consumers, scanned_functions)
                    
            # 扫描模块中的类方法
            for name, obj in mod.__dict__.items():
                if inspect.isclass(obj):
                    self._scan_class(obj, name, mod_name, topic_consumers, scanned_functions)
        return topic_consumers

    def _scan_function(self, obj, func_name, mod_name, topic_consumers, scanned_functions):
        """扫描单个函数"""
        scanned_functions.add(func_name)
        
        # 检查是否有消费者装饰器属性
        if hasattr(obj, "_is_kafka_consumer") and getattr(obj, "_is_kafka_consumer"):
            print(f"✅ 找到Kafka消费者函数: {mod_name}.{func_name}")
            consumer_config = getattr(obj, "_kafka_consumer_config")
            
            topic_consumers.append(
                self.register(
                    topic=getattr(obj, "_topic"),
                    handler=obj,
                    consumer_config=ConsumerConfig(
                        group_id=consumer_config.group_id,
                        consumer_type=consumer_config.consumer_type,
                        concurrency=consumer_config.concurrency,
                        auto_offset_reset=consumer_config.auto_offset_reset,
                        enable_auto_commit=consumer_config.enable_auto_commit,
                        max_poll_records=consumer_config.max_poll_records,
                    ),
                )
            )
        else:
            # 调试信息：打印所有函数看看
            if mod_name.startswith("service") and not func_name.startswith('_'):
                print(f"  📝 函数: {mod_name}.{func_name}")

    def _scan_class(self, cls, class_name, mod_name, topic_consumers, scanned_functions):
        """扫描类中的方法"""
        for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            full_name = f"{mod_name}.{class_name}.{method_name}"
            if full_name in scanned_functions:
                continue
                
            scanned_functions.add(full_name)
            
            if hasattr(method, "_is_kafka_consumer") and getattr(method, "_is_kafka_consumer"):
                print(f"✅ 找到Kafka消费者方法: {full_name}")
                consumer_config = getattr(method, "_kafka_consumer_config")
                
                topic_consumers.append(
                    self.register(
                        topic=getattr(method, "_topic"),
                        handler=method,
                        consumer_config=ConsumerConfig(
                            group_id=consumer_config.group_id,
                            consumer_type=consumer_config.consumer_type,
                            concurrency=consumer_config.concurrency,
                            auto_offset_reset=consumer_config.auto_offset_reset,
                            enable_auto_commit=consumer_config.enable_auto_commit,
                            max_poll_records=consumer_config.max_poll_records,
                        ),
                    )
                )

    def register(
        self, topic: str, handler: Callable, consumer_config: ConsumerConfig
    ) -> TopicConsumer:
        """注册消费者并返回 consumer_id"""
        consumer_id = f"consumer_{topic}_{uuid.uuid4().hex[:8]}"

        assert consumer_config
        topic_consumer = TopicConsumer(
            consumer_id=consumer_id,
            topic=topic,
            handler=handler,
            config=consumer_config,
        )

        # 存储到不同的索引中
        if topic not in self._topic_consumer:
            self._topic_consumer[topic] = topic_consumer
        self._consumer_instances[consumer_id] = topic_consumer

        self.logger.info(f"Registered consumer {consumer_id} for topic '{topic}'")
        return topic_consumer

    async def start(self, topic: str) -> Optional[TopicConsumer]:
        """启动指定 topic 的所有消费者"""
        if not self._topic_consumer.__contains__(topic):
            self.logger.warning(f"这个topic下没有消费者 '{topic}'")
            return

        topic_consumer = self._topic_consumer[topic]
        if (
            topic_consumer.status == ConsumerStatus.STARTING
            or topic_consumer.status == ConsumerStatus.RUNNING
        ):
            return topic_consumer
        try:
            topic_consumer.status = ConsumerStatus.STARTING
            consumer = AIOKafkaConsumer(
                topic_consumer.topic,
                bootstrap_servers=self.config.kafka_bootstrap_servers,
                group_id=topic_consumer.config.group_id,
                value_deserializer=lambda m: m.decode("utf-8"),
                enable_auto_commit=topic_consumer.config.enable_auto_commit,
                max_poll_records=topic_consumer.config.max_poll_records,
                **self.config.security_config,
            )
            await consumer.start()

            topic_consumer.consumer = consumer
            topic_consumer.status = ConsumerStatus.RUNNING
            # 启动消费任务
            for i in range(topic_consumer.config.concurrency):
                task = asyncio.create_task(self._consume_messages(topic_consumer, i))
                topic_consumer.tasks.append(task)
        except Exception as e:
            self.logger.error(
                f"Failed to start consumer {topic_consumer.consumer_id}: {e}"
            )
            topic_consumer.status = ConsumerStatus.STOPPED
        finally:
            return topic_consumer

    async def start_all(self):
        """启动所有生产者"""
        await asyncio.gather(
            *[self.start(topic) for topic in self._topic_consumer.keys()]
        )

    async def _consume_messages(
        self, topic_consumer: TopicConsumer, instance_index: int
    ):
        """消费消息"""
        consumer: Optional[AIOKafkaConsumer] = topic_consumer.consumer
        assert consumer
        try:
            async for message in consumer:
                try:
                    await topic_consumer.handler(
                        {
                            "data": message.value,
                            "topic": message.topic,
                            "partition": message.partition,
                            "offset": message.offset,
                            "consumer_id": topic_consumer.consumer_id,
                            "instance_index": instance_index,
                        }
                    )

                    if not topic_consumer.config.enable_auto_commit:
                        await consumer.commit()

                except Exception as e:
                    self.logger.error(
                        f"Error in consumer {topic_consumer.consumer_id} instance {instance_index}: {e}"
                    )

        except asyncio.CancelledError:
            self.logger.info(
                f"Consumer {topic_consumer.consumer_id} instance {instance_index} cancelled"
            )
        except Exception as e:
            self.logger.error(
                f"Consumer {topic_consumer.consumer_id} instance {instance_index} error: {e}"
            )
        finally:
            topic_consumer.status = ConsumerStatus.STOPPED

    async def stop(self, consumer_id: str):
        """停止指定消费者"""
        if consumer_id not in self._consumer_instances:
            return

        topic_consumer = self._consumer_instances[consumer_id]

        for task in topic_consumer.tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        if topic_consumer.consumer:
            await topic_consumer.consumer.stop()

        topic_consumer.status = ConsumerStatus.STOPPED
        self.logger.info(f"Stopped consumer {consumer_id}")

    async def stop_all(self):
        """停止所有生产者"""
        await asyncio.gather(
            *[
                self.stop(consumer.consumer_id)
                for consumer in self._topic_consumer.values()
            ]
        )
