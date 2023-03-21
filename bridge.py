import asyncio
import os
import time

from dotenv import load_dotenv
from multiprocessing import Process

from exporters import (
    check_poc_mysql_service,
    check_poc_nginx_service,
    check_poc_ruby_version,
    get_host_details,
    get_versions,
    ping_exporter,
)
from utils import imp_exp_func

load_dotenv()


async def run_tasks(hosts, headers, app_dirs):
    # define a list to keep track of all tasks
    tasks = []

    for host in hosts:
        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        # create a new task instance
        # exports versions of apps on the host
        task_1 = asyncio.create_task(
            get_versions(ip_address, user_name, app_dirs, headers)
        )
        # add the task to the list
        tasks.append(task_1)

        # create a new task instance
        # exports os details
        task_2 = asyncio.create_task(
            get_host_details(ip_address, user_name, headers)
        )
        # add the task to the list
        tasks.append(task_2)

        # create a new task instance
        # exports sites system poc services
        task_3 = asyncio.create_task(
            check_poc_mysql_service(ip_address, user_name, headers)
        )
        # add the task to the list
        tasks.append(task_3)

        task_4 = asyncio.create_task(
            check_poc_nginx_service(ip_address, user_name, headers)
        )
        # add the task to the list
        tasks.append(task_4)

        task_5 = asyncio.create_task(
            check_poc_ruby_version(ip_address, user_name, headers)
        )
        # add the task to the list
        tasks.append(task_5)

        # exports results of a ping of host
        # ping_exporter(ip_address, headers)

    # wait for all tasks to finish
    await asyncio.gather(*tasks)


async def init():
    hosts = imp_exp_func.get_data_from_api(os.getenv("IMPORTER_ENDPOINT"))
    headers = {
        "Content-type": "application/json",
        "Accept": "text/plain",
        "Authorization": os.getenv("EXPORTER_KEY"),
    }
    app_dirs = os.getenv("APP_DIRS").split(",")

    await run_tasks(hosts, headers, app_dirs)

    return True


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(init())
    end_time = time.time()
    runtime = end_time - start_time
    print("########################################################################################################")
    print("Runtime: ", runtime, " seconds")
