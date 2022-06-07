from curses import echo
import re
from fabric import Connection
import paramiko


def get_app_version(user_name: str, ip_address: str, app_dir: str) -> str:
    """gets version of an application running on remote server

    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server
        app_dir (str): directory of application

    Returns:
        str: version of application on remote server
    """
    try:
        run_cmd = Connection(
            f"{user_name}@{ip_address}").run(f"cd {app_dir} && git describe", hide=True, echo=True)

    except Exception as e:
        print(
            f"--- Failed to get version for {ip_address} for {app_dir} with exception: {e} ---")
        return "failed_to_get_version"

    return "{0.stdout}".format(run_cmd).strip()
    
def get_os_details(user_name: str, ip_address: str) -> str:
    """gets version of an application running on remote server
    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server
    Returns:
        str: version of application on remote server
    """
    try:
        run_cmd = Connection(
            f"{user_name}@{ip_address}").run(f"lsb_release -a", hide=True, echo=True)
        print(run_cmd)

    except Exception as e:
        print(
            f"--- Failed to get OS version for {ip_address} with exception: {e} ---")
        return "failed_to_get_version"
    return "{0.stdout}".format(run_cmd).strip()
