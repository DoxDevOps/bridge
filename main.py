from utils import exporter, importer, remote, net
import os
from dotenv import load_dotenv
load_dotenv()

# endpoint that has details (ip_address, username, name of host?) for remote
#! [TODO] can be nice to include functionality for csv or something similar
#! [TODO] functionality to switch between api and csv, a prefered way to bring in data can be defined in the .env
hosts = importer.get_hosts_from_api(os.getenv('IMPORTER_ENDPOINT'))

# list of app dirs as defined in the .env
app_dirs = os.getenv('APP_DIRS').split(',')

# when we sending data to a central repo, this is the default header
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

if not hosts:
    print("no hosts found")
    # exit the script, one can also consider quit() or exit() depending on the environment
    raise SystemExit

for count, host in enumerate(hosts):
    # depending on how your data is coming in, you may need to change this
    # to match your data structure
    ip_address = host["fields"]["ip_address"]
    user_name = host["fields"]["username"]
    site_name = host["fields"]["name"]

    # lets make sure we can get to the host
    if net.host_is_reachable(ip_address=ip_address):
        print(f"{site_name} is reachable")

        # get versions of all apps that are on the remote
        # basically, you are doing 'git describe' for all dirs that are provided within the .env
        # dirs that are not available on the remote host or where for whatever reason we didn't manage to get the version
        # will have a value, failed_to_get_version
        for app_dir in app_dirs:
            version = remote.get_app_version(user_name, ip_address, app_dir)

            # export app versions for remote
            if version != "failed_to_get_version":
                app_version = {"ip_address": ip_address, f"{app_dir}": version}

                # send data to central repo
                # currently, the implementation sends data per site per module (an app can have multiple modules)
                #! [TODO] one can wish to have a better performing implementation
                exporter.send_data(endpoint=os.getenv(
                    'EXPORTER_ENDPOINT'), payload=app_version, headers=headers)
    else:
        print(f"{site_name} is not reachable")
