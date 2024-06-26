def get_ip_address():
    import socket
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address
