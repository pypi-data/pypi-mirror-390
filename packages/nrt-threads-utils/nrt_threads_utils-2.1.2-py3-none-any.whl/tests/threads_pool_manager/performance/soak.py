import logging
from time import sleep

from nrt_time_utils.time_utils import MINUTE_MS, TimeUtil

from nrt_threads_utils.threads_pool_manager.enums import QueuePlacementEnum
from nrt_threads_utils.threads_pool_manager.threads_pool_manager import ThreadsPoolManager
from tests.threads_pool_manager.performance.performance_base import \
    AddTasksThread, _wait_and_verify_no_active_tasks
from tests.threads_pool_manager.threads_pool_manager_test_base import SleepSecPriorityThreadBase


class Sleep600SecPriority1Thread(SleepSecPriorityThreadBase):

    def __init__(self):
        super().__init__(10 * 60, 1)


class Sleep60SecPriority2Thread(SleepSecPriorityThreadBase):

    def __init__(self):
        super().__init__(60, 2)


class Sleep1SecPriority2Thread(SleepSecPriorityThreadBase):

    def __init__(self):
        super().__init__(1, 2)


class Sleep20SecPriority3Thread(SleepSecPriorityThreadBase):

    def __init__(self):
        super().__init__(1, 3)


EXECUTORS_POOL_SIZE = 30000
THREADS_AMOUNT_1 = 200000

threads_pool_manager = ThreadsPoolManager(executors_pool_size=EXECUTORS_POOL_SIZE)
threads_pool_manager.max_executors_extension_pool_size = 1000

WAIT_AFTER_T1_AND_T2_STARTED_MS = 10 * MINUTE_MS
WAIT_ALL_THREADS_FINISHED_MS = 240 * MINUTE_MS
WAIT_ALL_TASKS_FINISHED_MS = 240 * MINUTE_MS

try:
    logging.info('Starting threads pool manager')

    threads_pool_manager.start()

    for i in range(10):

        logging.info(f'Cycle number {i + 1}')

        add_tasks_thread_1 = \
            AddTasksThread(
                Sleep600SecPriority1Thread,
                'task_id_1',
                1,
                QueuePlacementEnum.AVOID_STARVATION_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        add_tasks_thread_2 = \
            AddTasksThread(
                Sleep60SecPriority2Thread,
                'task_id_2',
                2,
                QueuePlacementEnum.AVOID_STARVATION_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        add_tasks_thread_1.start()
        add_tasks_thread_2.start()

        start_time_ms = TimeUtil.get_current_date_ms()

        logging.info('Waiting for 10 minutes')

        while not TimeUtil.is_timeout_ms(start_time_ms, WAIT_AFTER_T1_AND_T2_STARTED_MS):

            logging.debug(f'Active tasks amount: {threads_pool_manager.active_tasks_amount}')
            logging.debug(f'Queue size: {threads_pool_manager.queue_size}')

            sleep(10)

        add_tasks_thread_3 = \
            AddTasksThread(
                Sleep1SecPriority2Thread,
                'task_id_3',
                2,
                QueuePlacementEnum.AVOID_STARVATION_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        add_tasks_thread_4 = \
            AddTasksThread(
                Sleep20SecPriority3Thread,
                'task_id_4',
                3,
                QueuePlacementEnum.AVOID_STARVATION_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        start_time_ms = TimeUtil.get_current_date_ms()

        while (add_tasks_thread_1.is_alive() or add_tasks_thread_2.is_alive()) \
                and not TimeUtil.is_timeout_ms(start_time_ms, WAIT_ALL_THREADS_FINISHED_MS):

            logging.debug(f'Active tasks amount: {threads_pool_manager.active_tasks_amount}')
            logging.debug(f'Queue size: {threads_pool_manager.queue_size}')

            sleep(10)

        _wait_and_verify_no_active_tasks(WAIT_ALL_TASKS_FINISHED_MS, threads_pool_manager)
finally:
    threads_pool_manager.shutdown()
    threads_pool_manager.join()
