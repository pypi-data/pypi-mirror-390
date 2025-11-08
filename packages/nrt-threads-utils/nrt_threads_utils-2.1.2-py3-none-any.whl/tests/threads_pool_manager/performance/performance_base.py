import logging
from threading import Thread
from time import sleep

from nrt_time_utils.time_utils import TimeUtil

from nrt_threads_utils.threads_pool_manager.enums import QueuePlacementEnum
from nrt_threads_utils.threads_pool_manager.tasks import ThreadTask
from nrt_threads_utils.threads_pool_manager.threads_pool_manager import \
    ThreadsPoolManager


def _wait_and_verify_no_active_tasks(timeout_ms: int, threads_pool_manager: ThreadsPoolManager):

    is_finished = False

    start_time_ms = TimeUtil.get_current_date_ms()

    while not TimeUtil.is_timeout_ms(start_time_ms, timeout_ms) and not is_finished:
        if threads_pool_manager.active_tasks_amount == 0:
            is_finished = True

        logging.debug(f'Active tasks amount: {threads_pool_manager.active_tasks_amount}')
        logging.debug(f'Queue size: {threads_pool_manager.queue_size}')

        sleep(10)

    assert is_finished, f'Active tasks amount is {threads_pool_manager.active_tasks_amount}'
    assert threads_pool_manager.queue_size == 0


class AddTasksThread(Thread):

    __task_id_prefix: str
    __priority: int
    __queue_placement: QueuePlacementEnum
    __amount: int
    __threads_pool_manager: ThreadsPoolManager

    def __init__(
            self,
            execution_class,
            task_id_prefix: str,
            priority: int,
            queue_placement: QueuePlacementEnum,
            amount: int,
            threads_pool_manager: ThreadsPoolManager):

        super().__init__()

        self._execution_class = execution_class
        self.__task_id_prefix = task_id_prefix
        self.__priority = priority
        self.__queue_placement = queue_placement
        self.__amount = amount
        self.__threads_pool_manager = threads_pool_manager

    def run(self):
        for i in range(self.__amount):
            task = self._execution_class()

            task_id = f'{self.__task_id_prefix}_{i}'

            if i % 1000 == 0:
                logging.debug(f'Adding task {task_id}')

            self.__threads_pool_manager.add_task(
                ThreadTask(task),
                task_id=task_id,
                priority=self.__priority,
                queue_placement=self.__queue_placement)

            self.__verify_in_adding_tasks_loop(task_id, self.__threads_pool_manager)

    @classmethod
    def __verify_in_adding_tasks_loop(
            cls, task_id: str, threads_pool_manager: ThreadsPoolManager):

        assert threads_pool_manager.queue_size >= 0
        assert threads_pool_manager.get_task(task_id=task_id), f'{task_id} not found'
        assert threads_pool_manager.is_task_exists(task_id=task_id)
        assert threads_pool_manager.queue is not None
        assert threads_pool_manager.executors_extension_pool_size >= 0
        assert threads_pool_manager.finished_tasks is not None
        assert threads_pool_manager.metrics is not None
        assert threads_pool_manager.active_tasks_amount >= 0
        assert not threads_pool_manager.is_all_executed
