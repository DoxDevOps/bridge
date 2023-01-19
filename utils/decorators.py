from functools import wraps
from .net import host_is_reachable


def check_if_host_is_reachable(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        try:
            if host_is_reachable(args[0]):
                return func(*args, **kwargs)
            else:
                print("host is not reachable")
        except:
            print("error")
    return decorated
