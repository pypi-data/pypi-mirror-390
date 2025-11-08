from threading import Thread
from time import sleep


class SleepSecPriorityThreadBase(Thread):
    __sleep_sec: int
    __priority: int

    def __init__(self, sleep_sec: int, priority: int):
        super().__init__()

        self.__sleep_sec = sleep_sec
        self.__priority = priority

    def run(self):
        sleep(self.__sleep_sec)

    @property
    def priority(self):
        return self.__priority
