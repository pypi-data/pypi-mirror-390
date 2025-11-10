from consumer.decorators import kafka_consumer

@kafka_consumer(topic="handle_topic", group_id="test")
def handle_topic(message_ctx: dict):
    print(f"收到消息: {message_ctx}")