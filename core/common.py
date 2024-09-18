import datetime
import os
import sys
import time
import traceback
import core.global_state as global_state
import threading
import requests



# A lock for writing log messages
_log_lock = threading.Lock()


def get_project_directory():
    """Returns the project directory hosted under ../user-data/."""

    project_directory = os.path.join(
        get_python_code_directory(), '..', 'user-data'
    )

    # Create the directory if it doesn't exist
    if not os.path.exists(project_directory):
        os.makedirs(project_directory)

    return project_directory


def get_python_code_directory():
    """Returns the directory where the current code is hosted."""

    return os.path.dirname(os.path.realpath(__file__))


def log(message: str):
    """Logs the message to `inspector.log` under the project directory, along with the timestamp."""

    # Add the timestamp to the message
    message = '[%s] %s' % (str(datetime.datetime.now()), message)

    with _log_lock:
        with open(os.path.join(get_project_directory(), 'inspector.log'), 'a') as f:
            f.write(message + '\n')



class SafeLoopThread(object):
    """
    A wrapper to repeatedly execute a function in a daemon thread; if the
    function crashes, automatically restarts the function.

    Usage:

    def my_func(a, b=1):
        pass

    SafeLoopThread(my_func, args=['a'], kwargs={'b': 2}, sleep_time=1)

    TODO: Rewrite this as a decorator.

    """
    def __init__(self, func, args=[], kwargs={}, sleep_time=1) -> None:

        self._func = func
        self._func_args = args
        self._func_kwargs = kwargs
        self._sleep_time = sleep_time

        th = threading.Thread(target=self._execute_repeated_func_safe)
        th.daemon = True
        th.start()

    def _repeat_func(self):
        """Repeatedly calls the function."""

        log('[SafeLoopThread] Starting %s %s %s' % (self._func, self._func_args, self._func_kwargs))

        while True:
            self._func(*self._func_args, **self._func_kwargs)
            if self._sleep_time:
                time.sleep(self._sleep_time)

    def _execute_repeated_func_safe(self):
        """Safely executes the repeated function calls."""

        while True:

            try:
                self._repeat_func()

            except Exception as e:

                err_msg = '=' * 80 + '\n'
                err_msg += 'Time: %s\n' % datetime.datetime.today()
                err_msg += 'Function: %s %s %s\n' % (self._func, self._func_args, self._func_kwargs)
                err_msg += 'Exception: %s\n' % e
                err_msg += str(traceback.format_exc()) + '\n\n\n'

                sys.stderr.write(err_msg + '\n')
                log(err_msg)

                time.sleep(self._sleep_time)


def get_os():
    """Returns 'mac', 'linux', or 'windows'. Raises RuntimeError otherwise."""

    os_platform = sys.platform

    if os_platform.startswith('darwin'):
        return 'mac'

    if os_platform.startswith('linux'):
        return 'linux'

    if os_platform.startswith('win'):
        return 'windows'

    raise RuntimeError('Unsupported operating system.')



def http_request(method='get', field_to_extract='', args=[], kwargs={}) -> str:
    """
    Issues an HTTP request and parse the returned contents.

    Returns the field_to_extract from the returned JSON object. If not, returns
    ''. If the request fails, raises IOError and logs the failure.

    """
    if method not in ['get', 'post']:
        raise RuntimeError('Unsupported method: %s' % method)

    # Make the request
    try:
        if method == 'get':
            r = requests.get(*args, **kwargs)
        else:
            r = requests.post(*args, **kwargs)
    except Exception as ex:
        log(f'[http_request] Error: request with args {args} failed to complete: {ex}')
        raise IOError

    # Check the status code
    if r.status_code != 200:
        log(f'[http_request] Error: request with args {args} failed with status code {r.status_code}')
        raise IOError

    # Parse the response as JSON
    try:
        response_dict = r.json()
    except Exception as ex:
        log(f'[http_request] Error: unable to parse the response as JSON: {ex} - {r.text}')
        raise IOError

    # Check if success
    if not response_dict['success']:
        err_msg = ''
        if 'error' in response_dict:
            err_msg = response_dict['error']
        # Ignore the most common error (which is not an error because it takes
        # time for the backend to analyze an IP address) so that we won't
        # overwhelm the log with this message
        if err_msg != 'No data for this ip_addr':
            log(f'[http_request] Error: request with args {args} did not succeed with error message: {err_msg}')
        raise IOError

    # Return the field
    if field_to_extract:
        if field_to_extract not in response_dict:
            log(f'[http_request] Error: request with args {args} did not return the field {field_to_extract}')
            raise IOError
        return response_dict[field_to_extract]

    return ''









