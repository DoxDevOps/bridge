from utils import imp_exp_func, remote, decorators
import os
from dotenv import load_dotenv
load_dotenv()


@decorators.check_if_host_is_reachable
def get_versions(ip_address: str, user_name: str, headers: dict) -> bool:

    for app_dir in os.getenv('APP_DIRS').split(','):

        version = remote.get_app_version(user_name, ip_address, app_dir)

        if version != "failed_to_get_version":

            app_version = {"ip_address": ip_address,
                           "app_dir": app_dir, "version": version}

            if not imp_exp_func.send_data(os.getenv('EXPORTER_ENDPOINT'), app_version, headers):

                return False

            return True
