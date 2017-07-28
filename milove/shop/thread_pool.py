from concurrent.futures import ThreadPoolExecutor

from django.conf import settings

_thread_pool = ThreadPoolExecutor(settings.THREAD_POOL_MAX_WORKER)


def go(func, *args, **kwargs):
    return _thread_pool.submit(func, *args, **kwargs)
