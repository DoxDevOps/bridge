import platform
import subprocess
from ipaddress import IPv4Address


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

def save_failed_ping(ip_address: IPv4Address, user_name: str, site_name: str):
    result = subprocess.run(['ping', '-c', '1', str(ip_address)], stdout=subprocess.PIPE)
    if result.returncode != 0:
        with open('failed_ping_ips.txt', 'a') as f:
            f.write(f"Failed ping from {user_name} at {site_name}: {ip_address}\n")
