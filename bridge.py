from utils import imp_exp_func
from exporters import get_host_details, get_versions, ping_exporter
import os
from dotenv import load_dotenv
load_dotenv()
import schedule
import time

def init():
    hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain','Authorization': os.getenv('EXPORTER_KEY')}
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
        get_host_details(ip_address, user_name, headers)

# run job every 3 hrs
# for now
init()
schedule.every(2).hours.do(init)
while True:
        schedule.run_pending()
        time.sleep(1)
