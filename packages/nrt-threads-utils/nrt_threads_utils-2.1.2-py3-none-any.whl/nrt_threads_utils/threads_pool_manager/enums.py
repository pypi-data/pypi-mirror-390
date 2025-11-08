from enum import Enum


class TaskTypeEnum(Enum):
    METHOD = 1
    PROCESS = 2
    THREAD = 3


class QueuePlacementEnum(Enum):
    STRICT_PRIORITY = 1
    AVOID_STARVATION_PRIORITY = 2


class TaskStateEnum(Enum):
    QUEUE = 1
    EXECUTORS_POOL = 2
    EXECUTED = 3
