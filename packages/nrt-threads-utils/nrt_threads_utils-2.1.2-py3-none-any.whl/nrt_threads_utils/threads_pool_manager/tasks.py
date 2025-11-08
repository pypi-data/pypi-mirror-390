import traceback
from abc import abstractmethod
from threading import Thread
from typing import Optional
from nrt_time_utils.time_utils import TimeUtil
from nrt_threads_utils.threads_pool_manager.enums import TaskStateEnum, TaskTypeEnum


class TaskBase:
    _start_date_ms: int
    _task_state: TaskStateEnum
    _exception: Optional[Exception] = None
    _stack_trace: Optional[str] = None

    def __init__(self):
        self._start_date_ms = 0
        self._task_state = TaskStateEnum.QUEUE

    @property
    def alive_date_ms(self) -> int:
        if self.start_date_ms:
            return TimeUtil.get_current_date_ms() - self.start_date_ms

        return 0

    @property
    def exception(self) -> Optional[Exception]:
        return self._exception

    @property
    def stack_trace(self) -> Optional[str]:
        return self._stack_trace

    @property
    def start_date_ms(self) -> int:
        return self._start_date_ms

    @start_date_ms.setter
    def start_date_ms(self, date_ms: int):
        self._start_date_ms = date_ms

    @property
    def task_state(self) -> TaskStateEnum:
        return self._task_state

    @task_state.setter
    def task_state(self, task_state: TaskStateEnum):
        self._task_state = task_state

    @abstractmethod
    def execute(self):
        raise NotImplementedError


class ThreadTask(TaskBase):
    __task: Thread

    def __init__(self, task: Thread):
        super().__init__()

        self.__task = task

    def execute(self):
        self.__task.start()
        self.__task.join()

    @property
    def task_instance(self) -> Thread:
        return self.__task


class MethodTask(TaskBase):
    __task: callable
    __args: tuple
    __kwargs: dict
    __result = None

    def __init__(self, task: callable, *args, **kwargs):
        super().__init__()

        self.__task = task
        self.__args = args
        self.__kwargs = kwargs

    def execute(self):
        try:
            self.__result = self.__task(*self.__args, **self.__kwargs)
        except Exception as e:
            self._exception = e
            self._stack_trace = traceback.format_exc()

    @property
    def result(self):
        if self.task_state != TaskStateEnum.EXECUTED:
            raise RuntimeError(f'Method task {self.__task} not executed yet')

        return self.__result


class TaskExecutor(Thread):
    __task: TaskBase
    __priority: int
    __avoid_starvation_flag: bool = False
    __task_id: Optional[str] = None

    def __init__(
            self,
            task: TaskBase,
            task_id: Optional[str] = None,
            priority: int = 1):

        super().__init__()

        self.__task = task
        self.__task_id = task_id
        self.__priority = priority

    @property
    def exception(self) -> Optional[Exception]:
        return self.__task.exception

    @property
    def stack_trace(self) -> Optional[str]:
        return self.__task.stack_trace

    def run(self):
        self.__task.start_date_ms = TimeUtil.get_current_date_ms()
        self.__task.execute()

    @property
    def avoid_starvation_flag(self) -> bool:
        return self.__avoid_starvation_flag

    @avoid_starvation_flag.setter
    def avoid_starvation_flag(self, flag: bool):
        self.__avoid_starvation_flag = flag

    @property
    def priority(self) -> int:
        return self.__priority

    @property
    def task(self) -> [MethodTask, ThreadTask]:
        return self.__task

    @property
    def task_type(self) -> TaskTypeEnum:
        if isinstance(self.__task, MethodTask):
            return TaskTypeEnum.METHOD

        if isinstance(self.task, ThreadTask):
            return TaskTypeEnum.THREAD

        raise ValueError(f'Task type of {self.task.__class__} not supported')

    @property
    def task_id(self) -> Optional[str]:
        return self.__task_id
