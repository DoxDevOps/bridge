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

        for each_password in _PASSWORDS_:
            try:
                ssh.connect(ip_address, username=user_name, password=each_password)
                stdin, stdout, stderr = ssh.exec_command(f"cd {app_dir} && git describe")
                result = stdout.read().splitlines()
                version = f"{result[0]}".split("'")[1]
                ssh.close()
                return version

            except Exception as e:
                print("An error occured: ", e)

    except Exception as e:
        print(f"--- Failed to get version for {ip_address} for {app_dir} with exception: {e} ---")
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
                ssh.connect(ip_address, username=user_name, password=each_password)
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

def get_host_remote_serial_number(user_name: str, ip_address: str) -> str:
    """gets serial number of the remote host

    Args:
        user_name (str): remote user name
        ip_address (str): ip address of remote server

    Returns:
        str: serial_number
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
                ssh.connect(ip_address, username=user_name, password=each_password)
                transport = ssh.get_transport()
                session = transport.open_session()
                session.set_combine_stderr(True)
                session.get_pty()
                #for testing purposes we want to force sudo to always to ask for password. because of that we use "-k" key
                session.exec_command("sudo dmidecode -s system-serial-number")
                stdin = session.makefile('wb', -1)
                stdout = session.makefile('rb', -1)
                #you have to check if you really need to send password here 
                stdin.write(each_password +'\n')
                stdin.flush()
                for line in stdout.read().splitlines():        
                    print ("#########################")
                    print(line)
                    print ("#########################")
                # # Linux command for system version inf
                # stdin, stdout, stderr = ssh.exec_command("cat /etc/os-release")
                # # Output command execution results
                # result = stdout.read().splitlines()
                # serial_number = f"{result[0]}".split("'")[1]
                # ssh.close()
                # return serial_number

            except Exception as e:
                print("An error occured: ", e)

    except Exception as e:
        print(
            f"--- Failed to get host system details for {ip_address} with exception: {e} ---")
        return "failed_to_get_host_system_details"

get_host_remote_serial_number(user_name='emruser', ip_address='10.40.11.3')