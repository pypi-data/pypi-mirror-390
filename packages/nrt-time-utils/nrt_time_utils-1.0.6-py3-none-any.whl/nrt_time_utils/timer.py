import inspect
import traceback
from dataclasses import dataclass
from threading import Lock
from typing import Optional

from nrt_time_utils.time_utils import TimeUtil


@dataclass
class Timer:
    start_date_ms: Optional[int] = None
    end_date_ms: Optional[int] = None
    result: any = None
    exception: Optional[Exception] = None
    stack_trace: Optional[str] = None

    @property
    def execution_time_ms(self) -> Optional[int]:
        return self.end_date_ms - self.start_date_ms if self.end_date_ms else None

    def __enter__(self):
        self.start_date_ms = TimeUtil.get_current_date_ms()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_date_ms = TimeUtil.get_current_date_ms()

        self.exception = exc_val

        if self.exception:
            self.stack_trace = traceback.format_exc()

    def __str__(self) -> str:
        return \
            f'Start date ms = {self.start_date_ms}.'\
            f' End date ms = {self.end_date_ms}.'\
            f' Execution time ms = {self.execution_time_ms}'


__max_keys: int = 100
__max_results_per_key: int = 10000

__lock = Lock()
__timer_results: dict[str, list[Timer]] = {}


def get_max_keys() -> int:
    return __max_keys


def set_max_keys(new_max_keys: int):
    global __max_keys
    __max_keys = new_max_keys


def get_max_results_per_key() -> int:
    return __max_results_per_key


def set_max_results_per_key(new_max_results_per_key: int):
    global __max_results_per_key
    __max_results_per_key = new_max_results_per_key


def reset_timer_results():
    with __lock:
        global __timer_results
        __timer_results = {}


def get_timer_results() -> dict:
    with __lock:
        return __timer_results.copy()


def method_timer(func, *args, **kwargs) -> Timer:
    timer_result = Timer()
    timer_result.start_date_ms = TimeUtil.get_current_date_ms()

    try:
        timer_result.result = func(*args, **kwargs)
    except Exception as e:
        timer_result.end_date_ms = TimeUtil.get_current_date_ms()
        timer_result.exception = e
        timer_result.stack_trace = traceback.format_exc()
    finally:
        if timer_result.end_date_ms is None:
            timer_result.end_date_ms = TimeUtil.get_current_date_ms()

    return timer_result


def timer(is_enabled: bool = True):

    def decorator(func):

        def wrapper(*args, **kwargs):
            timer_result = method_timer(func, *args, **kwargs)

            if is_enabled:
                func_file = inspect.getfile(func)
                func_qualname = func.__qualname__
                key = f'{func_file}:{func_qualname}'

                with __lock:
                    if __timer_results.get(key):
                        if len(__timer_results[key]) >= __max_results_per_key:
                            __timer_results[key].pop(0)

                        __timer_results[key].append(timer_result)
                    else:
                        if len(__timer_results) < __max_keys:
                            __timer_results[key] = [timer_result]

            if timer_result.exception:
                raise timer_result.exception

            return timer_result.result

        return wrapper

    return decorator
