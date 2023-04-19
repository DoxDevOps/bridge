from multiprocessing import Process
import time
from time import sleep
import schedule
from utils import imp_exp_func, net
from exporters import get_host_details, get_versions, ping_exporter, check_poc_mysql_service, check_poc_nginx_service
import os
from dotenv import load_dotenv
load_dotenv()

def site_operations(ip_address: str, user_name: str,  site_name: str, headers, app_dirs):
    processes = []
    # create a new process instance
    # exports versions of apps on the host
    process_1 = Process(target=get_versions, args=(
        ip_address, user_name, site_name, app_dirs, headers,))
    # start the process
    process_1.start()
    # add the process to the list
    processes.append(process_1)

    # create a new process instance
    # exports os details
    process_2 = Process(target=get_host_details,
                        args=(ip_address, user_name, headers,))
    # start the process
    process_2.start()
    # add the process to the list
    processes.append(process_2)

    # create a new process instance
    # exports sites system poc services
    process_3 = Process(target=check_poc_mysql_service,
                        args=(ip_address, user_name, headers,))
    # start the process
    process_3.start()
    # add the process to the list
    processes.append(process_3)

    # create a new process instance
    # exports status for system service
    process_4 = Process(target=check_poc_nginx_service,
                        args=(ip_address, user_name, headers,))
    # start the process
    process_4.start()
    # add the process to the list
    processes.append(process_4)

    process_5 = Process(target=net.save_failed_ping,
                        args=(ip_address, user_name, site_name,))
    process_5.start()
    processes.append(process_5)

    # exports results of a ping of host
    # ping_exporter(ip_address, headers)
    for process in processes:
        process.join()

    return True


def init():
    hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain', 'Authorization': os.getenv('EXPORTER_KEY')}
    app_dirs = os.getenv('APP_DIRS').split(',')
    # define a list to keep track of all processes
    processes = []

    for i, host in enumerate(hosts):

        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        process_m = Process(target=site_operations, args=(
            ip_address, user_name, site_name, app_dirs, headers,))
        # start the process
        process_m.start()
        # add the process to the list
        processes.append(process_m)
        
        # wait for 13 seconds after the 10th host
        if (i + 1) % 10 == 0:
            sleep(13)
        
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

