import socket
from .protocol import parse_message, build_message

def send_request(host='127.0.0.1', port=8080, message="Requesting text..."):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.sendall(build_message(message))
    data = s.recv(4096)
    s.close()
    return parse_message(data)
