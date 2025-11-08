import copy
from threading import Lock, Thread
from typing import Optional
from time import sleep
from nrt_collections_utils.list_utils import ListUtil
from nrt_threads_utils.threads_pool_manager.enums import \
    TaskStateEnum, QueuePlacementEnum, TaskTypeEnum
from nrt_threads_utils.threads_pool_manager.threads_pool_manager_exceptions import \
    FullQueueException
from nrt_threads_utils.threads_pool_manager.metrics import ThreadsPoolManagerMetrics
from nrt_threads_utils.threads_pool_manager.tasks import TaskExecutor, TaskBase


class ThreadsPoolManager(Thread):
    MAX_FINISHED_TASKS_LIST_SIZE = 100
    AVOID_STARVATION_AMOUNT = 10

    __threads_lock: Lock
    __metrics_lock: Lock
    __finished_tasks_lock: Lock

    __executors_pool: list
    __queue: list[TaskExecutor]
    __finished_tasks: list[TaskExecutor]

    __is_executors_shutdown: bool = False
    __is_shutdown: bool = False

    __max_finished_tasks_list_size: int = MAX_FINISHED_TASKS_LIST_SIZE
    __max_executors_pool_size: int
    __max_queue_size: int = 0
    __max_executors_extension_pool_size: int = 0
    __name: Optional[str] = None
    __executors_timeout_ms: int = 0

    __executors_extension_pool_size = 0

    __avoid_starvation_amount: int = AVOID_STARVATION_AMOUNT
    __avoid_starvation_counter: int = 0

    __metrics: ThreadsPoolManagerMetrics

    __temp_tasks_ids: list[str]

    def __init__(self, executors_pool_size: int = 1):
        super().__init__()

        self.__threads_lock = Lock()
        self.__metrics_lock = Lock()
        self.__finished_tasks_lock = Lock()
        self.__queue = []
        self.__finished_tasks = []
        self.__max_executors_pool_size = executors_pool_size
        self.__executors_pool = []
        self.__metrics = ThreadsPoolManagerMetrics()
        self.__temp_tasks_ids = []

    def add_task(
            self,
            task: TaskBase,
            task_id: Optional[str] = None,
            priority: int = 1,
            queue_placement: QueuePlacementEnum = QueuePlacementEnum.STRICT_PRIORITY):

        task_executor = TaskExecutor(task=task, task_id=task_id, priority=priority)

        with self.__threads_lock:
            self.__verify_queue_size()

            if queue_placement == QueuePlacementEnum.STRICT_PRIORITY:
                self.__add_task_strict_queue_placement(task_executor)
            elif queue_placement == QueuePlacementEnum.AVOID_STARVATION_PRIORITY:
                self.__add_task_avoid_starvation_queue_placement(task_executor)
            else:
                raise NotImplementedError('Queue placement not implemented')

            self.__update_max_queue_size_metrics()

    def get_task(self, task_id: str) -> Optional[TaskBase]:
        with self.__threads_lock:
            is_next_try = True

            while is_next_try:
                if task_id not in self.__temp_tasks_ids:
                    is_next_try = False

                for te in self.__executors_pool:
                    # te can be None until it will be removed from executors pool
                    if te and te.task_id == task_id:
                        return te.task

                for te in self.__queue:
                    if te.task_id == task_id:
                        return te.task

        return None

    def is_task_exists(self, task_id: str) -> bool:
        return self.get_task(task_id) is not None

    def run(self):
        while not self.__is_shutdown:
            self.__update_execution_metrics()

            if not self.is_executors_shutdown:
                is_execute = self.__get_next_task_from_queue_to_executors_pool()
            else:
                is_execute = False

            is_remove = self.__remove_dead_tasks_from_executors_pool()

            if not is_execute and not is_remove:
                sleep(.05)

    def reset_metrics(self):
        with self.__metrics_lock:
            self.__metrics = ThreadsPoolManagerMetrics()

    def shutdown(self):
        self.__is_shutdown = True

    def shutdown_executors(self):
        self.__is_executors_shutdown = True

    def start_executors(self):
        self.__is_executors_shutdown = False

    @property
    def active_tasks_amount(self) -> int:
        return len(self.__executors_pool)

    @property
    def avoid_starvation_amount(self) -> int:
        return self.__avoid_starvation_amount

    @property
    def avoid_starvation_task_index(self):
        for i, te in enumerate(reversed(self.__queue)):
            if te.avoid_starvation_flag:
                return len(self.__queue) - 1 - i

        return -1

    @avoid_starvation_amount.setter
    def avoid_starvation_amount(self, amount: int):
        self.__avoid_starvation_amount = amount

    @property
    def executors_extension_pool_size(self) -> int:
        return self.__executors_extension_pool_size

    @property
    def executors_timeout_ms(self) -> int:
        return self.__executors_timeout_ms

    @executors_timeout_ms.setter
    def executors_timeout_ms(self, timeout_ms: int):
        self.__executors_timeout_ms = timeout_ms

    @property
    def finished_tasks(self) -> list[TaskExecutor]:
        # lock is needed because there is a method that pop finished tasks
        with self.__finished_tasks_lock:
            finished_tasks = self.__finished_tasks.copy()
            self.__finished_tasks = []
            return finished_tasks

    @property
    def is_all_executed(self):
        with self.__threads_lock:
            return not (self.__executors_pool or self.__queue or self.__temp_tasks_ids)

    @property
    def is_executors_shutdown(self) -> bool:
        return self.__is_executors_shutdown

    @property
    def max_executors_extension_pool_size(self) -> int:
        return self.__max_executors_extension_pool_size

    @max_executors_extension_pool_size.setter
    def max_executors_extension_pool_size(self, size: int):
        self.__max_executors_extension_pool_size = size

    @property
    def max_executors_pool_size(self) -> int:
        return self.__max_executors_pool_size

    @max_executors_pool_size.setter
    def max_executors_pool_size(self, size: int):
        self.__max_executors_pool_size = size

    @property
    def max_finished_tasks_list_size(self) -> int:
        return self.__max_finished_tasks_list_size

    @max_finished_tasks_list_size.setter
    def max_finished_tasks_list_size(self, size: int):
        self.__max_finished_tasks_list_size = size

    @property
    def max_queue_size(self) -> int:
        return self.__max_queue_size

    @max_queue_size.setter
    def max_queue_size(self, size: int):
        self.__max_queue_size = size

    @property
    def metrics(self) -> ThreadsPoolManagerMetrics:
        with self.__metrics_lock:
            return copy.deepcopy(self.__metrics)

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, name: str):
        self.__name = name

    @property
    def queue(self) -> list[TaskExecutor]:
        return self.__queue.copy()

    @property
    def queue_size(self) -> int:
        return len(self.__queue)

    def __verify_queue_size(self):
        if self.queue_size >= self.max_queue_size > 0:
            raise FullQueueException(f'Queue size: {self.queue_size}')

    def __get_next_task_from_queue_to_executors_pool(self) -> bool:
        if len(self.__executors_pool) < self.max_executors_pool_size \
                or self.__increase_executors_extension_pool_size():

            task_executor = self.__get_next_task_executor()

            if task_executor is not None:
                task_executor.task.task_state = TaskStateEnum.EXECUTORS_POOL
                task_executor.start()
                self.__executors_pool.append(task_executor)

                if task_executor.task_id:
                    self.__temp_tasks_ids.remove(task_executor.task_id)

                return True

        return False

    def __increase_executors_extension_pool_size(self):
        if self.executors_extension_pool_size < self.max_executors_extension_pool_size \
                and len(self.__executors_pool) >= self.max_executors_pool_size \
                and self.__is_executor_timeout() \
                and self.queue_size:

            self.__executors_extension_pool_size += 1

            return True

        return False

    def __is_executor_timeout(self):
        return any(te and te.task.alive_date_ms > self.executors_timeout_ms
                   for te in self.__executors_pool)

    def __remove_dead_tasks_from_executors_pool(self):
        is_removed = False

        for i in range(len(self.__executors_pool)):
            if not self.__executors_pool[i].is_alive():

                self.__update_executed_tasks_counter_metrics(
                    self.__executors_pool[i].priority, self.__executors_pool[i].task_type)

                self.__executors_pool[i].task.task_state = TaskStateEnum.EXECUTED
                self.__add_task_executor_to_finished_tasks(self.__executors_pool[i])

                self.__executors_pool[i] = None

                if self.__executors_extension_pool_size > 0:
                    self.__executors_extension_pool_size -= 1

                is_removed = True

        self.__executors_pool = ListUtil.remove_none(self.__executors_pool)

        return is_removed

    def __add_task_executor_to_finished_tasks(self, task_executor: TaskExecutor):
        with self.__finished_tasks_lock:
            if len(self.__finished_tasks) >= self.max_finished_tasks_list_size:
                self.__finished_tasks.pop(0)

            self.__finished_tasks.append(task_executor)

    def __get_next_task_executor(self):
        with self.__threads_lock:
            if self.queue_size > 0:
                task_id = self.__queue[0].task_id

                if task_id:
                    self.__temp_tasks_ids.append(task_id)

                task_executor = self.__queue.pop(0)

                return task_executor

        return None

    def __add_task_strict_queue_placement(self, task: TaskExecutor, start_index: int = 0) -> int:

        for i, te in enumerate(self.__queue[start_index:], start=start_index):
            if te.priority < task.priority:
                self.__queue.insert(i, task)
                return i

        self.__queue.append(task)

        return -1

    def __add_task_avoid_starvation_queue_placement(self, task_executor: TaskExecutor):
        if self.__avoid_starvation_counter >= self.__avoid_starvation_amount:
            self.__add_task_avoid_starvation_counter_equal_to_amount(task_executor)
        else:
            self.__add_task_avoid_starvation_counter_gt_than_amount(task_executor)

    def __add_task_avoid_starvation_counter_gt_than_amount(self, task_executor: TaskExecutor):

        avoid_starvation_task_index = self.avoid_starvation_task_index

        if avoid_starvation_task_index >= 0:
            index = \
                self.__add_task_strict_queue_placement(
                    task_executor, avoid_starvation_task_index + 1)
        else:
            index = self.__add_task_strict_queue_placement(task_executor)

        if index != -1:
            self.__avoid_starvation_counter += 1

    def __add_task_avoid_starvation_counter_equal_to_amount(self, task_executor: TaskExecutor):

        task_executor.avoid_starvation_flag = True
        self.__update_avoid_starvation_counter_metrics()
        self.__avoid_starvation_counter = 0
        self.__queue.append(task_executor)

    def __update_execution_metrics(self):
        with self.__metrics_lock:
            for te in self.__executors_pool:
                if te and te.task.alive_date_ms > self.__metrics.max_execution_date_ms:
                    self.__metrics.max_execution_date_ms = te.task.alive_date_ms

    def __update_max_queue_size_metrics(self):
        with self.__metrics_lock:
            if self.queue_size > self.__metrics.max_queue_size:
                self.__metrics.max_queue_size = len(self.__queue)

    def __update_executed_tasks_counter_metrics(self, priority: int, task_type: TaskTypeEnum):

        with self.__metrics_lock:
            self.__metrics.executed_tasks_counter += 1

            if priority not in self.__metrics.tasks_priority_counter_dict:
                self.__metrics.tasks_priority_counter_dict[priority] = 1
            else:
                self.__metrics.tasks_priority_counter_dict[priority] += 1

            if task_type == TaskTypeEnum.METHOD:
                self.__metrics.executed_methods_counter += 1

                if priority not in self.__metrics.method_tasks_counter_dict:
                    self.__metrics.method_tasks_counter_dict[priority] = 1
                else:
                    self.__metrics.method_tasks_counter_dict[priority] += 1

            if task_type == TaskTypeEnum.THREAD:
                self.__metrics.executed_threads_counter += 1

                if priority not in self.__metrics.thread_tasks_counter_dict:
                    self.__metrics.thread_tasks_counter_dict[priority] = 1
                else:
                    self.__metrics.thread_tasks_counter_dict[priority] += 1

    def __update_avoid_starvation_counter_metrics(self):
        with self.__metrics_lock:
            self.__metrics.avoid_starvation_counter += 1
