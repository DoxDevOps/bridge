import platform
import subprocess
import pickle
import os
import paramiko


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


def updatePswrdDict(key, value):
    filename = 'utils/pswd_ao_dict.pickle'

    # check if file exists and is not empty
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        # load the dictionary from file
        with open(filename, 'rb') as f:
            my_dict = pickle.load(f)
    else:
        # create an empty dictionary
        my_dict = {}

    # update or insert a key-value pair
    my_dict[key] = value

    # save the updated dictionary to file
    with open(filename, 'wb') as f:
        pickle.dump(my_dict, f)


def getPswrd(ip_address):
    filename = 'utils/pswd_ao_dict.pickle'
    # load the dictionary from file
    with open(filename, 'rb') as f:
        my_dict = pickle.load(f)

        # get the value for the given key, or return False if the key is not in the dictionary
    value = my_dict.get(ip_address, False)
    if value is False:
        return False
    else:
        return value


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