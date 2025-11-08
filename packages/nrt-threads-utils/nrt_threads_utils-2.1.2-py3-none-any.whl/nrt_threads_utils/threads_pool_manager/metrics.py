from dataclasses import dataclass
from typing import Optional


@dataclass
class ThreadsPoolManagerMetrics:
    avoid_starvation_counter: int = 0
    executed_methods_counter: int = 0
    executed_tasks_counter: int = 0
    executed_threads_counter: int = 0
    max_execution_date_ms: int = 0
    max_queue_size: int = 0
    method_tasks_counter_dict: Optional[dict[int, int]] = None
    tasks_priority_counter_dict: Optional[dict[int, int]] = None
    thread_tasks_counter_dict: Optional[dict[int, int]] = None

    def __init__(self):
        self.method_tasks_counter_dict = {}
        self.tasks_priority_counter_dict = {}
        self.thread_tasks_counter_dict = {}
