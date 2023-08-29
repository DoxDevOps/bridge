from utils import net, imp_exp_func, decorators
from multiprocessing import Process
import os
from dotenv import load_dotenv
import random
import time
load_dotenv()

def seed():
    hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
    # Shuffle the array in place
    random.shuffle(hosts)

    processes = []

    for host in hosts:

        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        p_process = Process(target= net.ssh_copy_id,
                            args=(user_name, ip_address,))
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
    if seed():
        end_time = time.time()
        runtime = end_time - start_time
        print("########################################################")
        print("Runtime: ", runtime, " seconds")