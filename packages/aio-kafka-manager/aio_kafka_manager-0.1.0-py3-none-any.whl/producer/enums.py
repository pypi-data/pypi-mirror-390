from enum import StrEnum


class ProducerType(StrEnum):
    DEFAULT = "default"
    HIGH_THROUGHPUT = "high_throughput"
    TRANSACTIONAL = "transactional"

class ProducerStatus(StrEnum):
    NOT_STARTED = "not_started"
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"

