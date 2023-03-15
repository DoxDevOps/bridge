from curses import echo
import re
from fabric import Connection
import paramiko
from config.config import data

_PASSWORDS_ = data["PASSWORD"]


def get_app_version(user_name: str, ip_address: str, app_dir: str) -> str:
    """gets version of an application running on remote server

    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server
        app_dir (str): directory of application

    Returns:
        str: version of application on remote server
    """
    try:
        ssh = paramiko.SSHClient()
        # ssh.load_host_keys('/home/username/.ssh/known_hosts')
        # ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Establish a connection with a hard coded pasword
        # a private key will be used soon
        # AUTO SSH IS NEEDED ON THIS

        # tracker
        count = 0

        for each_password in _PASSWORDS_:
            try:
                ssh.connect(ip_address, username=user_name,
                            password=each_password)
                stdin, stdout, stderr = ssh.exec_command(
                    f"cd {app_dir} && git describe")
                result = stdout.read().splitlines()
                version = f"{result[0]}".split("'")[1]

                # Close the connection
                ssh.close()

                collection = [version]
                return collection

            except Exception as e:
                print("An error occured: ", e)
                count += 1
                if count == len(_PASSWORDS_):
                    # Write failed IP addresses to a file
                    with open("failed_ips.txt", "a") as f:
                        f.write(ip_address + "\n")

    except Exception as e:
        print(
            f"--- Failed to get version for {ip_address} for {app_dir} with exception: {e} ---")
        return "failed_to_get_version"


def get_host_system_details(user_name: str, ip_address: str) -> str:
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
        ssh = paramiko.SSHClient()
        # ssh.load_host_keys('/home/username/.ssh/known_hosts')
        # ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Establish a connection with a hard coded pasword
        # a private key will be used soon
        # AUTO SSH IS NEEDED ON THIS

        for each_password in _PASSWORDS_:
            try:
                ssh.connect(ip_address, username=user_name,
                            password=each_password)
                # Linux command for system version inf
                stdin, stdout, stderr = ssh.exec_command("cat /etc/os-release")
                # Output command execution results
                result = stdout.read().splitlines()
                # string of both os name and version
                inputstring = f"{result[0]} {result[1]}"
                # array of both os anme and version
                collection = re.findall('"([^"]*)"', inputstring)

                # Linux command for cpu utilazation command
                get_cpu_uti_cmd = "top -bn2 | grep '%Cpu' | tail -1 | grep -P '(....|...) id,'|awk '{print  100-$8 }'"
                # executing command for writing to stdout
                stdin, stdout, stderr = ssh.exec_command(get_cpu_uti_cmd)
                # getting value for cpu utilzation
                cpu_utilization = stdout.read().splitlines()[0]
                cpu_utilization = f"{cpu_utilization}"
                collection.append(cpu_utilization.split("'")[1])

                # Linux command for HDD utilazation command
                get_hdd_uti_cmd = "df -h -t ext4"
                # executing command for writing to stdout
                stdin, stdout, stderr = ssh.exec_command(get_hdd_uti_cmd)
                # getting values for hdd utilaztion
                hdd_utilazation = stdout.read().splitlines()[1]
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
                stdin, stdout, stderr = ssh.exec_command(get_ram_uti_cmd)
                # getting values for hdd utilaztion
                ram_utilazation = stdout.read().splitlines()[1]
                ram_utilazation = f"{ram_utilazation}".split()
                # total_ram
                collection.append(ram_utilazation[1])
                # used_ram
                collection.append(ram_utilazation[2])
                # remaining_ram
                collection.append(ram_utilazation[6])

                # Close the connection
                ssh.close()
                return collection
            except Exception as e:
                print("An error occured: ", e)

    except Exception as e:
        print(
            f"--- Failed to get host system details for {ip_address} with exception: {e} ---")
        return "failed_to_get_host_system_details"


def check_and_start_mysql_service(remote_host, ssh_username):
    for password in _PASSWORDS_:
        try:
            # Set up a SSH client and connect to the remote host
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(remote_host, username=ssh_username, password=password)

            # Run the systemctl command to check the status of the MySQL service
            cmd = "systemctl status mysql.service"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read()

            # Check the output for the service status
            if b"Active: active" in output:
                print("MySQL service is running")
                status = "running"
            else:
                print("MySQL service is not running")
                status = "not_running"

                # # If the service is not running, try to start it
                # print("MySQL service is not running. Attempting to start...")
                # cmd = "systemctl start mysql.service"
                # stdin, stdout, stderr = ssh.exec_command(cmd)
                # output = stdout.read()

                # # Check the output for errors
                # if stderr:
                #     print(f"Error starting MySQL service: {stderr}")
                #     status = "error"
                # else:
                #     print("MySQL service started successfully")
                #     status = "started"

            # Close the SSH connection
            ssh.close()
            break  # Stop looping once a successful connection is established
        except paramiko.AuthenticationException as e:
            print(f"Authentication failed with password: {e}")
            status = "auth_error"
        except paramiko.SSHException as e:
            print(
                f"Unable to establish SSH connection with password: {e}")
            status = "ssh_error"
        except Exception as e:
            print(f"An error occurred with password: {e}")
            status = "unknown_error"

    return status


def check_and_start_nginx_service(remote_host, ssh_username):
    for password in _PASSWORDS_:
        try:
            # Set up an SSH client and connect to the remote host
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(remote_host, username=ssh_username, password=password)

            # Run the systemctl command to check the status of the nginx service
            cmd = "systemctl status nginx.service"
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read()

            # Check the output for the service status
            if b"Active: active" in output:
                print("nginx service is running")
                status = "running"
            else:
                print("nginx service is not running")
                status = "not_running"
                
                # # If the service is not running, try to start it
                # print("Attempting to start nginx service...")
                # cmd = "systemctl start nginx.service"
                # stdin, stdout, stderr = ssh.exec_command(cmd)
                # output = stdout.read()

                # # Check the output for errors
                # if stderr:
                #     print(f"Error starting nginx service: {stderr}")
                #     status = "error"
                # else:
                #     print("nginx service started successfully")
                #     status = "started"

            # Close the SSH connection
            ssh.close()
            break  # Stop looping once a successful connection is established
        except paramiko.AuthenticationException as e:
            print(f"Authentication failed with password: {e}")
            status = "auth_error"
        except paramiko.SSHException as e:
            print(f"Unable to establish SSH connection with password: {e}")
            status = "ssh_error"
        except Exception as e:
            print(f"An error occurred with password: {e}")
            status = "unknown_error"

    return status
