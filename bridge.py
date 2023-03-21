import asyncio
import time
import schedule
from utils import imp_exp_func
from exporters import get_host_details, get_versions, ping_exporter, check_poc_mysql_service, check_poc_nginx_service, check_poc_ruby_version
import os
from dotenv import load_dotenv
load_dotenv()


async def init():
    hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
    headers = {'Content-type': 'application/json',
               'Accept': 'text/plain', 'Authorization': os.getenv('EXPORTER_KEY')}
    app_dirs = os.getenv('APP_DIRS').split(',')

    # create a list of coroutines to run in parallel
    coroutines = []
    for host in hosts:
        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        # create a coroutine to export versions of apps on the host
        coro_1 = get_versions(ip_address, user_name, app_dirs, headers)
        coroutines.append(coro_1)

        # create a coroutine to export os details
        coro_2 = get_host_details(ip_address, user_name, headers)
        coroutines.append(coro_2)

        # create a coroutine to export sites system poc services
        coro_3 = check_poc_mysql_service(ip_address, user_name, headers)
        coroutines.append(coro_3)

        coro_4 = check_poc_nginx_service(ip_address, user_name, headers)
        coroutines.append(coro_4)

        coro_5 = check_poc_ruby_version(ip_address, user_name, headers)
        coroutines.append(coro_5)

        # create a coroutine to export results of a ping of host
        # coro_6 = ping_exporter(ip_address, headers)
        # coroutines.append(coro_6)

    # run all coroutines in parallel
    await asyncio.gather(*coroutines)

    return True


if __name__ == '__main__':
    start_time = time.time()

    asyncio.run(init())

    end_time = time.time()
    runtime = end_time - start_time
    print("########################################################################################################")
    print("Runtime: ", runtime, " seconds")