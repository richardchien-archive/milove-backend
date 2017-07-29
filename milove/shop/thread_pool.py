import atexit
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from sched import scheduler

from django.conf import settings


class _Scheduler(object):
    def __init__(self):
        self._should_stop = False
        self._thread = None
        self._sched = scheduler()

    def _loop(self):
        while not self._should_stop:
            if not self._sched.empty():
                _thread_pool.submit(self._sched.run, blocking=False)
            time.sleep(0.25)

    def start(self):
        self._should_stop = False
        if not self._thread or not self._thread.is_alive():
            self._thread = Thread(target=self._loop, daemon=True)
            self._thread.start()

    def shutdown(self):
        self._should_stop = True
        if self._thread and self._thread.is_alive():
            self._thread.join()
            self._thread = None

    def submit(self, delay, func, *args, **kwargs):
        return self._sched.enter(delay, 1, func, args, kwargs)


_thread_pool = ThreadPoolExecutor(settings.THREAD_POOL_MAX_WORKER)
_scheduler = _Scheduler()
_scheduler.start()


def async_run(func, *args, **kwargs):
    return _thread_pool.submit(func, *args, **kwargs)


def delay_run(delay, func, *args, **kwargs):
    return _scheduler.submit(delay, func, *args, **kwargs)


def _shutdown():
    _scheduler.shutdown()
    _thread_pool.shutdown()


atexit.register(_shutdown)
