from multiprocessing import Process
import time
from time import sleep
import schedule
from utils import imp_exp_func, net
from exporters import get_host_details, get_versions, ping_exporter, check_poc_mysql_service, check_poc_nginx_service,check_poc_ruby_version
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
    count = 0

    for host in hosts:

        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        # create a new process instance
        # exports os details
        p_process = Process(target=get_host_details,
                            args=(ip_address, user_name, headers,))
        # start the process
        p_process.start()
        # add the process to the list
        processes.append(p_process)

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
