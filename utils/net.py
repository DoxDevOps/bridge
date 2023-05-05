import platform
import subprocess
from ipaddress import IPv4Address
import asyncio
import paramiko
import redis


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

def save_failed_ping(ip_address: IPv4Address, user_name: str, site_name: str):
    result = subprocess.run(['ping', '-c', '1', str(ip_address)], stdout=subprocess.PIPE)
    if result.returncode != 0:
        with open('failed_ping_ips.txt', 'a') as f:
            f.write(f"Failed ping from {user_name} at {site_name}: {ip_address}\n")

class AsyncParamikoSSHClient(paramiko.SSHClient):
    
    def __init__(self, host, username, password):
        super().__init__()
        self.host = host
        self.username = username
        self.password = password

    async def clsConnect(self):
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self._connect, self.host, self.username, self.password)
        await future

    def _connect(self, host, username, password):
        # self.connect(host, username, password)
        self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connect(hostname=host, username=username, password=password, port=22)

    async def send_command(self, command):
        channel = self.exec_command(command)
        stdin, stdout, stderr = channel
        output = stdout.read()
        self.close()
        return output

    async def receive_command(self, command):
        channel = await self.open_channel('session')
        await channel.exec_command(command)
        output = await channel.read_until_eof()
        channel.close()
        return output

# async def test_connect():
#     # Create a new AsyncParamikoSSHClient object.
#     client = AsyncParamikoSSHClient('server_ip', 'server_name', 'password')

#     # Connect to the remote host.
#     await client.clsConnect()

#     # Send a command to the remote host.
#     output = await client.send_command('ls')

#     # Print the output of the command.
#     print(output)

#     # Close the connection.
#     client.close()

# if __name__ == '__main__':
#     # Run the main function async
#     asyncio.run(test_connect())


# class RedisCls():
#     def __init__(self):
#         self.host = 'localhost'
#         self.port = 6379
#         self.db = 0
#         self.redis = redis.Redis(host=self.host, port=self.port, db=self.db)

#     def updatePswrdDict(self, key, value):
#         # update or insert a key-value pair
#         self.redis.set(key, value)

#     def getPswrd(self, ip_address):
#         # get the value for the given key, or return False if the key is not in Redis
#         try:
#             value = self.redis.get(ip_address)

#             if value is None:
#                 return False
#             else:
#                 return value.decode('utf-8')
#         except Exception as e:
#             return False


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
