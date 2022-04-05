from utils import importer, remote, net

hosts = importer.get_hosts_from_api(
    "http://10.44.0.52/sites/api/v1/get_sites")


if hosts:
    for count, host in enumerate(hosts):
        # depending on how your data is coming in you may need to change this
        # to match your data structure
        ip_address = host["fields"]["ip_address"]
        user_name = host["fields"]["username"]
        site_name = host["fields"]["name"]

        if net.host_is_reachable(ip_address):
            print(f"{site_name} is reachable")
            print(
                f"{site_name} version: {remote.get_app_version(user_name, ip_address, '/var/www/BHT-EMR-API')}")
        else:
            print(f"{site_name} is not reachable")
