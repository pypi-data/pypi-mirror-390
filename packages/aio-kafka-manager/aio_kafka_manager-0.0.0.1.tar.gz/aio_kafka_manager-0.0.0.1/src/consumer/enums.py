from enum import StrEnum

class ConsumerType(StrEnum):
    SINGLE = "single"
    GROUP = "group"
    BROADCAST = "broadcast"

class ConsumerStatus(StrEnum):
    NOT_STARTED = "not_started"
    STARTING = "starting"
    RUNNING = "running"
    STOPPED = "stopped"

