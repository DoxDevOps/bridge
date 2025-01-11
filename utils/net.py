import platform
import subprocess
from ipaddress import IPv4Address
import asyncio
import paramiko
import redis
import os
import asyncssh
import socket
from . import decorators2
import re
from dotenv import load_dotenv
load_dotenv()

def host_is_reachable(ip_address, port=22):
    sock = None
    try:
        # Create a socket object
        sock = socket.create_connection((ip_address, port), timeout=5)
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    except Exception as e:
        if sock:
            sock.close()
        raise e

def get_service_name(service):
    parts = service.split('.')
    first_part = parts[0]
    return first_part.capitalize()

def extract_distrib_version(input_string):
    match = re.search(r'Distrib\s([\d.]+)', input_string.decode('utf-8'))
    if match:
        return match.group(1)
    else:
        return None

def extract_version_number(input_string):
    match = re.search(r'Ver\s(\d+(?:\.\d+)+)', input_string.decode('utf-8'))
    if match:
        return match.group(1)
    else:
        return None

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

    def _connect(self, host, username, password):
        # self.connect(host, username, password)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(hostname=host, username=username, password=password, port=22)

    def _connect_key_based(self, host, username):
        try:
            self.load_system_host_keys()
            self.set_missing_host_key_policy(paramiko.WarningPolicy())
            
            # Check common key locations
            key_paths = [
                ("~/.ssh/id_ed25519", paramiko.Ed25519Key),
                ("~/.ssh/id_rsa", paramiko.RSAKey),
                ("~/.ssh/id_ecdsa", paramiko.ECDSAKey),
                ("~/.ssh/id_dsa", paramiko.DSSKey)
            ]
            
            # Override with environment variable if set
            if "SSH_PRIVATE_KEY_PATH" in os.environ:
                custom_path = os.environ["SSH_PRIVATE_KEY_PATH"]
                # Add the custom path to the start of our list
                key_paths.insert(0, (custom_path, None))  # None means we'll detect type
                
            connected = False
            last_exception = None
            
            for key_path, key_type in key_paths:
                try:
                    full_path = os.path.expanduser(key_path)
                    if not os.path.exists(full_path):
                        continue
                        
                    print(f"Attempting connection to {host} with key at {full_path}")
                    
                    # If key_type is None (custom path), try all key types
                    if key_type is None:
                        key_types = [paramiko.Ed25519Key, paramiko.RSAKey, 
                                paramiko.ECDSAKey, paramiko.DSSKey]
                    else:
                        key_types = [key_type]
                    
                    # Try each possible key type for this file
                    for kt in key_types:
                        try:
                            mykey = kt.from_private_key_file(full_path)
                            self.connect(hostname=host, username=username, 
                                    pkey=mykey, port=22)
                            connected = True
                            print(f"Successfully connected using {full_path}")
                            return True
                        except (paramiko.SSHException, Exception) as e:
                            last_exception = e
                            continue
                            
                except Exception as e:
                    last_exception = e
                    continue
                    
            if not connected:
                # If we got here, no connection was successful
                with open("setpolicykey.txt", "a") as file:
                    file.write(f"ssh {username}@{host}\n")
                error_msg = str(last_exception) if last_exception else "No valid keys found"
                print(f"connect key based error: {error_msg} for HOST: {host}")
                return False
                
        except Exception as e:
            with open("setpolicykey.txt", "a") as file:
                file.write(f"ssh {username}@{host}\n")
            print(f"connect key based error: {str(e)} for HOST: {host}")
            return False

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

from redis.asyncio import Redis

class RedisCls():
    def __init__(self):
        self.host = 'localhost'
        self.port = 6379
        self.db = 0
        self.redis = None

    async def connect(self):
        # connect to Redis asynchronously
        self.redis = await Redis(host=self.host, port=self.port, db=self.db)

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
            # Check if we can authenticate with password
            password = asyncio.run(check_if_password_works(remote_host=ip_address, ssh_username=username))
            if not password:
                print(f"Could not authenticate with password for {username}@{ip_address}")
                return False

            # Define possible key paths and types
            key_paths = [
                ("~/.ssh/id_ed25519", "ssh-ed25519"),
                ("~/.ssh/id_rsa", "ssh-rsa"),
                ("~/.ssh/id_ecdsa", "ecdsa-sha2-nistp256"),
                ("~/.ssh/id_dsa", "ssh-dss")
            ]

            # Try each key type
            for private_key_path, key_type in key_paths:
                private_key_path = os.path.expanduser(private_key_path)
                public_key_path = f"{private_key_path}.pub"

                # If we find a valid public key, use it
                if os.path.exists(public_key_path):
                    try:
                        # Read the public key
                        with open(public_key_path, "r") as pubkey_file:
                            public_key = pubkey_file.read().strip()

                        # Try to add the key
                        print(f"Attempting to copy {key_type} public key to {username}@{ip_address}")
                        asyncio.run(add_public_key_to_authorized_keys(
                            ip_address, username, password, public_key))
                        print(f"Successfully copied {key_type} public key to remote server's authorized_keys")
                        return True

                    except Exception as e:
                        print(f"Failed to copy {key_type} key: {str(e)}")
                        continue

            # If we get here, no keys were successfully copied
            print(f"No valid SSH keys found for {username}@{ip_address}")
            return False

        except Exception as e:
            print(f"Error in ssh_copy_id for {username}@{ip_address}: {str(e)}")
            return False
    else:
        print(f"Host {ip_address} is not reachable")
        return False


async def add_public_key_to_authorized_keys(ip_address, username, password, public_key):
    client = AsyncParamikoSSHClient(host=ip_address, username=username)
    
    try:
        await client.clsConnectWithPass(password=password)
        await client.send_sudo_command(password, 'sudo chmod 700 ~/.ssh')
        await client.send_sudo_command(password, 'sudo chmod 600 ~/.ssh/authorized_keys')
        sftp = await client.custom_open_sftp()
        sftp.put(os.path.expanduser("~/.ssh/id_ed25519")+'.pub', '' + 'yts')
        await client.send_sudo_command(password, 'echo "$(cat yts)" >> ~/.ssh/authorized_keys')
        await client.send_sudo_command(password, 'sudo rm yts')
        sftp.close()
        client.close()
    except Exception as e:
        print(f"eerror: {e}")
        sftp.close()
        client.close()
    finally:
        sftp.close()
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
            
            return str(password).strip()
        except paramiko.SSHException as e:
            print("Unable to establish SSH connection:", str(e))
        except Exception as e:
            print(e)
        finally:
            client.close()

def filter_unique_lines(input_filename, output_filename):
    unique_lines = set()

    try:
        with open(input_filename, "r") as input_file:
            for line in input_file:
                stripped_line = line.strip()
                if stripped_line not in unique_lines:
                    unique_lines.add(stripped_line)
    except FileNotFoundError:
        print(f"File '{input_filename}' not found.")
        return
    
    with open(output_filename, "w") as output_file:
        for line in unique_lines:
            output_file.write(f"{line}\n")