"""
Executes a function with deferred results.

Example:

def my_function():
    time.sleep(5)
    return 'hello'


deferred_action.execute(my_function, args=(,), kwargs={}, ttl=2) # returns nothing
deferred_action.execute(my_function, args=(,), kwargs={}, ttl=2) # returns 'hello'

"""
import time
import threading
import traceback
import queue
from core.common import log


_lock = threading.Lock()

_queue = [None]

# Maps a function key to the actual results
_result_dict = dict()

# A dict of pending functions -> their job_ix
_pending_func_dict = dict()

# Maps a function key to the max time where the result is valid
_ttl_dict = dict()

# Keeps track of where we are in the queue
_progress_dict = {
    'total_job_count': 0,
    'latest_completed_job_index': 0
}


class NoResultYet(Exception):
    pass


def _worker():

    while True:

        func_key, func, args, kwargs, ttl, job_ix = _queue[0].get()

        if args is None:
            args = tuple()

        if kwargs is None:
            kwargs = dict()

        # Execute the function
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            log('[deferred_action] Exception in {}: {} - traceback: {}'.format(
                func_key, e, traceback.format_exc())
            )
        else:
            with _lock:
                # Update the result
                _result_dict[func_key] = result
                _ttl_dict[func_key] = time.time() + ttl
        finally:
            with _lock:
                del _pending_func_dict[func_key]
                _progress_dict['latest_completed_job_index'] = job_ix



def execute(func, args=None, kwargs=None, ttl=5, custom_function_key=None):
    """
    Executes a function with deferred results.

    :param func: The function to execute.
    :param args: The arguments to pass to the function.
    :param kwargs: The keyword arguments to pass to the function.
    :return: The function's (earlier) results; raises NoResultYet if the function hasn't finished running yet.

    """
    if custom_function_key is None:
        func_key = repr((func, args, kwargs))
    else:
        func_key = custom_function_key

    with _lock:

        # If the previous results are still valid, just return them
        try:
            if _ttl_dict[func_key] > time.time():
                return _result_dict[func_key]
        except KeyError:
            pass

        # At this point, the previous results are invalid, or there are no
        # previous results. We need to execute the function (if it is not
        # already running).
        if func_key not in _pending_func_dict:
            # Keep track of the progress
            job_ix = _progress_dict['total_job_count'] + 1
            _progress_dict['total_job_count'] += 1
            # Enqueue the function
            _pending_func_dict[func_key] = job_ix
            _queue[0].put((func_key, func, args, kwargs, ttl, job_ix))

        # The function must be pending now. Return any previous results even if
        # they're no longer valid.
        try:
            return _result_dict[func_key]
        except KeyError:
            # Show any pending progress
            pending_job_count = _pending_func_dict[func_key] - _progress_dict['latest_completed_job_index']
            raise NoResultYet(pending_job_count)


def my_test_function():

    print('                        * my_test_function started')
    time.sleep(3)
    print('                        * my_test_function finished')
    return int(time.time())



def test():

    for t in range(20):
        print(f't={t}: Calling my_test_function')
        try:
            result = execute(my_test_function, args=tuple(), kwargs={})
        except NoResultYet as pending_job_count:
            print(f' -> No result yet, {pending_job_count} pending jobs')
        else:
            print(' -> Result: {}'.format(result))
        time.sleep(1)


# Start the worker thread automatically
with _lock:
    if _queue[0] is None:
        # Start the worker thread exactly once
        _queue[0] = queue.Queue()
        for _ in range(1):
            threading.Thread(
                target=_worker,
                daemon=True
            ).start()


if __name__ == '__main__':
    test()