from multiprocessing import Process
import time
import schedule
from utils import imp_exp_func, general_utils
from exporters import get_versions
import os
from dotenv import load_dotenv
load_dotenv()


def init():
    hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain', 'Authorization': os.getenv('EXPORTER_KEY')}
    app_dirs = os.getenv('APP_DIRS').split(',')
    # define a list to keep track of all processes
    processes = []
    hosts = general_utils.randomize_list(hosts)

    for host in hosts:

        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        # create a new process instance
        # exports versions of apps on the host
        process_1 = Process(target=get_versions, args=(
            ip_address, user_name, app_dirs, headers,))
        # start the process
        process_1.start()
        # add the process to the list
        processes.append(process_1)

    # wait for all processes to finish
    for process in processes:
        process.join()

    return True


if __name__ == '__main__':
    start_time = time.time()
    if init():
        end_time = time.time()
        runtime = end_time - start_time
        print("########################################################################################################")
        print("Runtime: ", runtime, " seconds")
