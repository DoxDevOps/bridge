from utils import imp_exp_func
from exporters import get_versions
import os
from dotenv import load_dotenv
load_dotenv()

hosts = imp_exp_func.get_data_from_api(os.getenv('IMPORTER_ENDPOINT'))
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

for host in hosts:

    ip_address = host["fields"]["ip_address"]
    user_name = host["fields"]["username"]
    site_name = host["fields"]["name"]

    get_versions(ip_address, user_name, headers)
