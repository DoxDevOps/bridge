from functools import wraps
from .net import host_is_reachable
from .net2 import host_is_reachable2


def check_if_host_is_reachable(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if host_is_reachable(args[0]):
            return func(*args, **kwargs)
        else:
            print("host is not reachable")
    return decorated

def check_if_host_is_reachable2(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if host_is_reachable2(args[0]):
            return func(*args, **kwargs)
        else:
            print("host is not reachable")
    return decorated