from multiprocessing import Process
import time
import schedule
from utils import imp_exp_func
from exporters import get_host_details, get_versions, ping_exporter
import os
from dotenv import load_dotenv
load_dotenv()


def init():
    hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain', 'Authorization': os.getenv('EXPORTER_KEY')}
    app_dirs = os.getenv('APP_DIRS').split(',')

    for host in hosts:

        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        # create a new process instance
        # exports versions of apps on the host
        process_1 = Process(target=get_versions, args=(
            ip_address, user_name, headers,))
        # start the process
        process_1.start()

        # create a new process instance
        # exports os details
        process_2 = Process(target=get_host_details,
                            args=(ip_address, user_name, headers,))
        # start the process
        process_2.start()

        # exports results of a ping of host
        # ping_exporter(ip_address, headers)


if __name__ == '__main__':
    # run job every 2 hrs
    # for now
    init()
    schedule.every(2).hours.do(init)
    while True:
        schedule.run_pending()
        time.sleep(1)
