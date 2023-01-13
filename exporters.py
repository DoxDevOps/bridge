from utils import imp_exp_func, remote, decorators, net
import os
from dotenv import load_dotenv
load_dotenv()


@decorators.check_if_host_is_reachable
def get_versions(ip_address: str, user_name: str, app_dirs: list, headers: dict) -> bool:

    for app_dir in app_dirs:

        print(
            f"*** Starting to export version details for {app_dir} for host {ip_address}")

        version = remote.get_app_version(user_name, ip_address, app_dir)

        if version != "failed_to_get_version":

            app_version = {"ip_address": ip_address,
                           "app_dir": app_dir, "version": version}

            if not imp_exp_func.send_data(os.getenv('EXPORTER_ENDPOINT'), app_version, headers):

                return False

            return True


def ping_exporter(ip_address: str, headers: dict) -> bool:

    status = "up"

    if not net.host_is_reachable(ip_address):

        status = "down"

    uptime = {"ip_address": ip_address, "status": status}

    if not imp_exp_func.send_data(os.getenv('PING_EXPORTER_ENDPOINT'), uptime, headers):

        return False

    return True


@decorators.check_if_host_is_reachable
def get_host_details(ip_address: str, user_name: str, headers: dict) -> bool:

    print(
        f"*** Starting to export host system details for host {ip_address}")

    details = remote.get_host_system_details(user_name, ip_address)

    if type(details) == list:

        hdd_used_in_percentiles = (int(''.join(filter(str.isdigit, details[5]))) /
                                        int(''.join(filter(str.isdigit, details[3])))) * 100

        host_details = {"ip_address": ip_address,
                        "os_name": details[0],
                        "os_version": details[1],
                        "cpu_utilization": details[2],
                        "hdd_total_storage": details[3],
                        "hdd_remaining_storage": details[4],
                        "hdd_used_storage": details[5],
                        "hdd_remaining_in_percentiles": f"{int(hdd_used_in_percentiles)}%",
                        "total_ram": details[7],
                        "used_ram": details[8],
                        "remaining_ram": details[9]
                        }
        
        print(host_details)

        if not imp_exp_func.send_data(os.getenv('SYSTEM_UTI_ENDPOINT'), host_details, headers):

            return False

        return True
