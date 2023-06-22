import platform
import subprocess
import pickle
import os
import paramiko
import threading
import redis


def host_is_reachable(ip_address: str) -> bool:
    """checks if remote host is reachable

        Args:
            ip_address (str): ip address of remote server

        Returns:
            bool: True if remote host is reachable, False otherwise
        """

    param = '-n' if platform.system().lower() == 'windows' else '-c'

    if subprocess.call(['ping', param, '1', ip_address]) != 0:
        return False

    return True


# create a Redis client
r = redis.Redis(host='localhost', port=6379, db=0)

def updatePswrdDict(key, value):
    # update or insert a key-value pair
    # r.set(key, value)
    True

def getPswrd(ip_address):
    # get the value for the given key, or return False if the key is not in Redis
    # value = r.get(ip_address)

    # if value is None:
    #     return False
    # else:
    #     return value.decode('utf-8')
    return False


def is_password_valid(host, username, password):
    """Check if the given password works by trying to connect to a remote server"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host, username=username, password=password)
        ssh.close()
        return True
    except (paramiko.AuthenticationException, paramiko.SSHException) as e:
        ssh.close()
        return False
