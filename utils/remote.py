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


def get_host_os_name_and_version(user_name: str, ip_address: str) -> str:
    """gets version of operating system running on remote server

    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server

    Returns:
        str: version of operating system on remote server
    """
    try:

        ssh = paramiko.SSHClient()
        # ssh.load_host_keys('/home/username/.ssh/known_hosts')
        # ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Establish a connection with a hard coded pasword
        # a private key will be used soon
        ssh.connect(ip_address, username=user_name, password='PASSWORD')
        # Enter the Linux command
        stdin, stdout, stderr = ssh.exec_command("cat /etc/os-release")
        # Output command execution results
        result = stdout.read().splitlines()
        # string of both os name and version
        inputstring = f"{result[0]} {result[1]}"
        # array of both os anme and version
        collection = re.findall('"([^"]*)"', inputstring)
        # Close the connection
        ssh.close()

    except Exception as e:
        print(
            f"--- Failed to get os_name and os_version for {ip_address} with exception: {e} ---")
        return "failed_to_get_os_name_and_version"

    return collection
