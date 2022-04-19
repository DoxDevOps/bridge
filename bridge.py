from utils import imp_exp_func
from exporters import get_versions
import os
from dotenv import load_dotenv
load_dotenv()

os_name = 'nul'
os_version = 'nul'

for key, value in os.environ.items():
    #print('{}: {}'.format(key, value))
    if key == 'XDG_SESSION_DESKTOP':
        os_name = value
    if key == 'XDG_SESSION_TYPE':
        os_version = value

#check in terminal
print("OS name: ", os_name)
print("OS version: ", os_version)

print(os.getenv('HOME'))

hosts = imp_exp_func.get_data_from_api(os.getenv('HOME'))
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
app_dirs = os.getenv('APP_DIRS').split(',')

for host in hosts:

    ip_address = host["fields"]["ip_address"]
    user_name = host["fields"]["username"]
    site_name = host["fields"]["name"]

    get_versions(ip_address, user_name, app_dirs, headers)
