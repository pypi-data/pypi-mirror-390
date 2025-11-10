from consumer.decorators import kafka_consumer
from producer.manager import AIOKafkaProducerManager


def main():
    from kafka_manager import AIOKafkaManager
    import asyncio
    asyncio.run(AIOKafkaManager().startup())
    # asyncio.run(send_messages())
    asyncio.run(send_message())
    asyncio.run(asyncio.sleep(10))
    asyncio.run(AIOKafkaManager().shutdown())
    
async def send_message():
    await AIOKafkaProducerManager().send_message(topic="handle_topic", message={
            "name": "test"
        }, key="")

async def send_messages():
    await AIOKafkaProducerManager().send_messages(topic="handle_topic", messages=[{
            "name": "test"
        }], key="", headers=[])


if __name__ == "__main__":
    main()