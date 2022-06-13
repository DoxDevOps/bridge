import os
import platform
from utils import decorators,net,imp_exp_func
import subprocess
from dotenv import load_dotenv
load_dotenv()

@decorators.check_if_host_is_reachable
def ping_exporter(ip_address: str, headers: dict) ->bool :

    status = "up"

    if not net.host_is_reachable(ip_address):

        status = "down"

    uptime = {"ip_address": ip_address, "status": status}

    if not imp_exp_func.send_data(os.getenv('PING_EXPORTER_ENDPOINT'), uptime, headers):

        return False

    return True

hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
for host in hosts:

    ip_address = host["fields"]["ip_address"]
    user_name = host["fields"]["username"]
    site_name = host["fields"]["name"]

    # exports results of a ping of host
    ping_exporter(ip_address, headers, )

