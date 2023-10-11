import socket

def host_is_reachable2(ip_address, port=22):
    try:
        # Create a socket object
        sock = socket.create_connection((ip_address, port), timeout=5)
        # Close the socket
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False