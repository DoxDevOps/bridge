from utils import imp_exp_func
from exporters import get_os_details, get_versions, ping_exporter
import os
from dotenv import load_dotenv
load_dotenv()

hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
app_dirs = os.getenv('APP_DIRS').split(',')

for host in hosts:

    ip_address = host["fields"]["ip_address"]
    user_name = host["fields"]["username"]
    site_name = host["fields"]["name"]

    # exports versions of apps on the host
    get_versions(ip_address, user_name, app_dirs, headers)

    # exports results of a ping of host
    ping_exporter(ip_address, headers)

    # exports os details
    get_os_details(ip_address, user_name, headers)

# for test
#get_os_details('10.43.156.9', 'meduser', headers)
