import logging
from time import sleep
from nrt_time_utils.time_utils import TimeUtil, MINUTE_MS
from nrt_threads_utils.threads_pool_manager.enums import QueuePlacementEnum
from tests.threads_pool_manager.performance.performance_base import \
    AddTasksThread, _wait_and_verify_no_active_tasks
from nrt_threads_utils.threads_pool_manager.threads_pool_manager import ThreadsPoolManager
from tests.threads_pool_manager.threads_pool_manager_test_base import SleepSecPriorityThreadBase


class Sleep15SecPriority1Thread(SleepSecPriorityThreadBase):

    def __init__(self):
        super().__init__(15, 1)


class Sleep20SecPriority2Thread(SleepSecPriorityThreadBase):

    def __init__(self):
        super().__init__(20, 2)


EXECUTORS_POOL_SIZE = 4000
THREADS_AMOUNT_1 = 15000


def test_threads_pool_manager_strict_priority_performance():

    threads_pool_manager = ThreadsPoolManager(executors_pool_size=EXECUTORS_POOL_SIZE)
    threads_pool_manager.max_executors_extension_pool_size = 100
    threads_pool_manager.executors_timeout_ms = 40

    try:
        logging.debug('Starting threads pool manager')

        threads_pool_manager.start()

        add_tasks_thread_1 = \
            AddTasksThread(
                Sleep15SecPriority1Thread,
                'task_id_1',
                1,
                QueuePlacementEnum.STRICT_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        add_tasks_thread_2 = \
            AddTasksThread(
                Sleep20SecPriority2Thread,
                'task_id_2',
                2,
                QueuePlacementEnum.STRICT_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        add_tasks_thread_1.start()
        add_tasks_thread_2.start()

        timeout_ms = 30 * MINUTE_MS

        start_time_ms = TimeUtil.get_current_date_ms()

        while (add_tasks_thread_1.is_alive() or add_tasks_thread_2.is_alive()) \
                and not TimeUtil.is_timeout_ms(start_time_ms, timeout_ms):
            logging.debug(f'Active tasks amount: {threads_pool_manager.active_tasks_amount}')
            logging.debug(f'Queue size: {threads_pool_manager.queue_size}')

            sleep(10)

        assert not add_tasks_thread_1.is_alive(), 'Add Tasks Thread 1 is still alive'
        assert not add_tasks_thread_2.is_alive(), 'Add Tasks Thread 2 is still alive'

        wait_timeout_ms = 30 * MINUTE_MS

        _wait_and_verify_no_active_tasks(wait_timeout_ms, threads_pool_manager)

    finally:
        logging.debug('Shutting down threads pool manager')
        threads_pool_manager.shutdown()
        logging.debug('Joining threads pool manager')
        threads_pool_manager.join()
        logging.debug('Threads pool manager joined')


def test_threads_pool_manager_avoid_starvation_priority_performance():

    threads_pool_manager = ThreadsPoolManager(executors_pool_size=EXECUTORS_POOL_SIZE)
    threads_pool_manager.max_executors_extension_pool_size = 100
    threads_pool_manager.avoid_starvation_amount = 100
    threads_pool_manager.executors_timeout_ms = 40

    try:
        logging.debug('Starting threads pool manager')

        threads_pool_manager.start()

        add_tasks_thread_1 = \
            AddTasksThread(
                Sleep15SecPriority1Thread,
                'task_id_1',
                1,
                QueuePlacementEnum.AVOID_STARVATION_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        add_tasks_thread_2 = \
            AddTasksThread(
                Sleep20SecPriority2Thread,
                'task_id_2',
                2,
                QueuePlacementEnum.AVOID_STARVATION_PRIORITY,
                THREADS_AMOUNT_1,
                threads_pool_manager)

        add_tasks_thread_1.start()
        add_tasks_thread_2.start()

        timeout_ms = 30 * MINUTE_MS

        start_time_ms = TimeUtil.get_current_date_ms()

        while (add_tasks_thread_1.is_alive() or add_tasks_thread_2.is_alive()) \
                and not TimeUtil.is_timeout_ms(start_time_ms, timeout_ms):
            logging.debug(f'Active tasks amount: {threads_pool_manager.active_tasks_amount}')
            logging.debug(f'Queue size: {threads_pool_manager.queue_size}')

            sleep(10)

        assert not add_tasks_thread_1.is_alive(), 'Add Tasks Thread 1 is still alive'
        assert not add_tasks_thread_2.is_alive(), 'Add Tasks Thread 2 is still alive'

        wait_timeout_ms = 30 * MINUTE_MS

        _wait_and_verify_no_active_tasks(wait_timeout_ms, threads_pool_manager)
    finally:
        logging.debug('Shutting down threads pool manager')
        threads_pool_manager.shutdown()
        logging.debug('Joining threads pool manager')
        threads_pool_manager.join()
        logging.debug('Threads pool manager joined')
