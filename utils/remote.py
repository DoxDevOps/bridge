from curses import echo
import re
import paramiko
import os
import asyncio
from .net import AsyncParamikoSSHClient, RedisCls, get_service_name, extract_distrib_version, extract_version_number
from dotenv import load_dotenv
load_dotenv()

async def get_host_system_details(user_name: str, ip_address: str) -> str:
    """gets version of operating system running on remote host
       gets storage stats of remote host
       gets ram stats of remote host

    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server

    Returns:
        list: [os_name,
               os_version,
               cpu_utilization,
               hdd_total_storage,
               hdd_remaing_storage,
               hdd_used_storage,
               hdd_remaing_in_percentiles,
               total_ram,
               used_ram,
               remaining_ram
            ]
    """
    try:
        app_dirs = os.getenv('APP_DIRS').split(',')
        service_names = os.getenv('SERVICE_NAMES').split(',')
        client = await conect_to_remote_host(ip_address, user_name)
        if isinstance(client,AsyncParamikoSSHClient):
            print(f"*** Starting to export host system details for host {ip_address}")
            try:
                await client.clsConnect()
                # Linux command for system version inf
                cmd = "cat /etc/os-release"
                output = await client.send_command(cmd)
                
                # Output command execution results
                result = output.splitlines()
                # string of both os name and version
                inputstring = f"{result[0]} {result[1]}"
                # array of both os anme and version
                collection = re.findall('"([^"]*)"', inputstring)

                
                # Linux command for cpu utilazation command
                get_cpu_uti_cmd = "top -bn2 | grep '%Cpu' | tail -1 | grep -P '(....|...) id,'|awk '{print  100-$8 }'"
                # executing command for writing to stdout
                stdout  = await client.send_command(get_cpu_uti_cmd)
                
                # getting value for cpu utilzation
                cpu_utilization = stdout.splitlines()[0]
                cpu_utilization = f"{cpu_utilization}"
                collection.append(cpu_utilization.split("'")[1])

                
                # Linux command for HDD utilazation command
                get_hdd_uti_cmd = "df -h -t ext4"
                # executing command for writing to stdout
                stdout = await client.send_command(get_hdd_uti_cmd)
                  
                # getting values for hdd utilaztion
                hdd_utilazation = stdout.splitlines()[1]
                hdd_utilazation = f"{hdd_utilazation}".split()
                # total_storage
                collection.append(hdd_utilazation[1])
                # remaining_storage
                collection.append(hdd_utilazation[2])
                # used_storage
                collection.append(hdd_utilazation[3])
                # remaining_storage_percentile
                collection.append(hdd_utilazation[4])

                
                # Linux command for RAM utilazation command
                get_ram_uti_cmd = "free -h"
                # executing command for writing to stdout
                stdout = await client.send_command(get_ram_uti_cmd)
                
                # getting values for hdd utilaztion
                ram_utilazation = stdout.splitlines()[1]
                ram_utilazation = f"{ram_utilazation}".split()
                # total_ram
                collection.append(ram_utilazation[1])
                # used_ram
                collection.append(ram_utilazation[2])
                # remaining_ram
                collection.append(ram_utilazation[6])

                min_collection = []
                for app_dir in app_dirs:
                    
                    git_describe_cmd = f"cd {app_dir} && git describe"
                    stdout = await client.send_command(git_describe_cmd)

                    result = stdout.splitlines()
                    try:
                        version = f"{result[0]}".split("'")[1]
                    except Exception as e:
                        version = ''

                    if version:
                        app_version = {"ip_address": ip_address,
                                    "app_dir": app_dir,
                                        "version": version
                                    }
                        min_collection.append(app_version)
                
                collection.append(min_collection)
                
                minutre_collection = []
                for service_name in service_names:
                    status = ""
                    
                    # Run the systemctl command to check the status of the MySQL service
                    cmd = "systemctl status "+service_name
                    output = await client.send_command(cmd)
                    
                    # Check the output for the service status
                    if b"Active: active" in output:
                        status = "running"
                    else:
                        status = "not_running"

                    _data_ = {
                            "ip_address": ip_address,
                            "service_name": get_service_name(service_name),
                            "status": status
                        }
                    minutre_collection.append(_data_)

                    if service_name == 'mysql.service':
                        service_name = service_name.replace(".service", "")
                        cmd = service_name+" --version"
                        output = await client.send_command(cmd)

                        version = extract_distrib_version(output) if b"Distrib" in output else extract_version_number(output)
                        if version:
                            app_version = {
                                "ip_address": ip_address,
                                "app_dir": '/var/www/mysql',
                                "version": version
                            }
                            min_collection.append(app_version)

                collection.append(minutre_collection)

                client.close()
                return collection
            except Exception as e:
                client.close()
                print("An error occured fn(get_host_system_details): ", str(e)+" ip_address: ssh "+user_name+"@"+ip_address)

    except Exception as e:
        print(f"--- Failed to get host system details for {ip_address} with exception: {e} ---")
        return "failed_to_get_host_system_details"

# retuns AsyncParamikoSSHClient instance
async def conect_to_remote_host(remote_host, ssh_username):
    try:
        client = AsyncParamikoSSHClient(host=remote_host, username=ssh_username)
        await client.clsConnect()
        return client
    except paramiko.SSHException as e:
        print("Unable to establish SSH connection:", str(e))
    except Exception as e:
        print("conect to remote host error:", str(e))