import platform
import subprocess
from ipaddress import IPv4Address
import asyncio
import paramiko
import redis
import os
import asyncssh
from . import decorators2
from dotenv import load_dotenv
load_dotenv()

def host_is_reachable(ip_address: str) -> bool:
    """checks if remote host is reachable

        Args:
            ip_address (str): ip address of remote server

        Returns:
            bool: True if remote host is reachable, False otherwise
        """

    param = '-n' if platform.system().lower() == 'windows' else '-c'

    if subprocess.call(['ping', param, '1', ip_address]) != 0:
        return False

    return True

def get_service_name(service):
    parts = service.split('.')
    first_part = parts[0]
    return first_part.capitalize()

def save_failed_ping(ip_address: IPv4Address, user_name: str, site_name: str):
    result = subprocess.run(['ping', '-c', '1', str(ip_address)], stdout=subprocess.PIPE)
    if result.returncode != 0:
        with open('failed_ping_ips.txt', 'a') as f:
            f.write(f"Failed ping from {user_name} at {site_name}: {ip_address}\n")

class AsyncParamikoSSHClient(paramiko.SSHClient):
    
    def __init__(self, host, username):
        super().__init__()
        self.host = host
        self.username = username

    async def clsConnect(self):
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self._connect_key_based, self.host, self.username)
        await future

    async def clsConnectWithPass(self, password):
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self._connect, self.host, self.username, password)
        await future

    def _connect_key_based(self, host, username):
        self.load_system_host_keys()
        self.set_missing_host_key_policy(paramiko.WarningPolicy())

        private_key_path = os.path.expanduser("~/.ssh/id_rsa")  # Update this path if needed
        mykey = paramiko.RSAKey(filename=private_key_path)

        self.connect(hostname=host, username=username, pkey=mykey, port=22)

    def _connect(self, host, username, password):
        # self.connect(host, username, password)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(hostname=host, username=username, password=password, port=22)

    async def send_command(self, command):
        channel = self.exec_command(command)
        stdin, stdout, stderr = channel
        output = stdout.read()
        # self.close()
        return output
    
    async def send_sudo_command(self, password, command):
        sudo_command = f"echo \"{password}\" | sudo -S "+command
        channel = self.exec_command(sudo_command)
        stdin, stdout, stderr = channel
        decoded_stderr = stderr.read().decode("utf-8")  # Decode the stdout bytes into a string
        if decoded_stderr:
            # print(f"ERRor:\n{decoded_stderr}")
            True
        output = stdout.read()
        # self.close()
        return output
    
    async def custom_open_sftp(self):
        channel = self.open_sftp()
        return channel

    async def receive_command(self, command):
        channel = await self.open_channel('session')
        await channel.exec_command(command)
        output = await channel.read_until_eof()
        channel.close()
        return output

import aioredis

class RedisCls():
    def __init__(self):
        self.host = 'localhost'
        self.port = 6379
        self.db = 0
        self.redis = None

    async def connect(self):
        # connect to Redis asynchronously
        self.redis = await aioredis.Redis(host=self.host, port=self.port, db=self.db)

    async def updatePswrdDict(self, key, value):
        # update or insert a key-value pair asynchronously
        await self.redis.set(key, value)

    async def getPswrd(self, ip_address):
        # get the value for the given key asynchronously, or return False if the key is not in Redis
        try:
            value = await self.redis.get(ip_address)

            if value is None:
                return False
            else:
                return value.decode('utf-8')
        except Exception as e:
            return False

def ssh_copy_id(username, ip_address):
    if host_is_reachable(ip_address):
        try:
            password = asyncio.run(check_if_password_works(remote_host=ip_address, ssh_username=username))
            if (password):
                # Generate an SSH key pair (if not already generated)
                private_key_path = os.path.expanduser("~/.ssh/id_rsa")
                public_key_path = f"{private_key_path}.pub"

                # if not os.path.exists(private_key_path) or not os.path.exists(public_key_path):
                #     key = asyncio.run(asyncssh.generate_private_key("ssh-rsa"))
                #     with open(private_key_path, "w") as private_key_file:
                #         private_key_file.write(key.export_private_key("openssh").decode())

                #     with open(public_key_path, "w") as public_key_file:
                #         public_key_file.write(key.export_public_key("openssh").decode())

                # Read the public key
                with open(public_key_path, "r") as pubkey_file:
                    public_key = pubkey_file.read().strip()

                asyncio.run(add_public_key_to_authorized_keys(ip_address, username, password, public_key))

                print("Public key copied to remote server's authorized_keys.")
        except Exception as e:
            print(f"Error: {e}")


async def add_public_key_to_authorized_keys(ip_address, username, password, public_key):
    client = AsyncParamikoSSHClient(host=ip_address, username=username)
    
    try:
        await client.clsConnectWithPass(password=password)
        await client.send_sudo_command(password, 'sudo chmod 700 ~/.ssh')
        await client.send_sudo_command(password, 'sudo chmod 600 ~/.ssh/authorized_keys')
        sftp = await client.custom_open_sftp()
        sftp.put(os.path.expanduser("~/.ssh/id_rsa")+'.pub', '' + 'yts')
        await client.send_sudo_command(password, 'echo "$(cat yts)" >> ~/.ssh/authorized_keys')
        await client.send_sudo_command(password, 'sudo rm yts')
        sftp.close()
        client.close()
    except Exception as e:
        print(f"eerror: {e}")
        client.close()
    finally:
        client.close()


async def check_if_password_works(remote_host, ssh_username):
    redisInstance = RedisCls()
    await redisInstance.connect()
    redisPassword = await redisInstance.getPswrd(remote_host)

    # Use Redis password if available, otherwise iterate through password list
    _PASSWORDS_ = os.getenv('PASSWORDS')
    passwords = _PASSWORDS_.split(',')

    # Step 1: Remove unwanted characters (square brackets and single quotes) from the passwords
    password_list = [password.strip("['").strip("']") for password in passwords]
    password_list = [password.replace("'", "").strip("")
                    for password in password_list]
    passwords_to_try = [redisPassword] if redisPassword else password_list

    for password in passwords_to_try:
        try:
            client = AsyncParamikoSSHClient(host=remote_host, username=ssh_username)
            
            await client.clsConnectWithPass(password=str(password).strip())
            await redisInstance.updatePswrdDict(remote_host, str(password).strip())
            print(password)
            return str(password).strip()
        except paramiko.SSHException as e:
            print("Unable to establish SSH connection:", str(e))
        except Exception as e:
            print(e)
        finally:
            client.close()