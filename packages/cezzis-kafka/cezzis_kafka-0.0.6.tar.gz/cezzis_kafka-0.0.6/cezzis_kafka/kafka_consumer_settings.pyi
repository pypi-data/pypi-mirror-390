from _typeshed import Incomplete

class KafkaConsumerSettings:
    consumer_id: Incomplete
    bootstrap_servers: Incomplete
    consumer_group: Incomplete
    topic_name: Incomplete
    num_consumers: Incomplete
    def __init__(self, consumer_id: int, bootstrap_servers: str, consumer_group: str, topic_name: str, num_consumers: int = 1) -> None: ...
