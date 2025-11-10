import socket

HEADER = "TXTP/1.0\r\n"

def start_server(host: str = "0.0.0.0", port: int = 9090, text: str = "Hello from TXTP!"):
    """
    Start a TXTP server that listens for connections and sends a fixed text
    response with a TXTP header to any incoming request.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(5)
        print(f"[TXTP] Server listening on {host}:{port}")

        while True:
            conn, addr = server.accept()
            with conn:
                print(f"[TXTP] Connection from {addr}")
                data = conn.recv(1024)
                if not data:
                    continue
                response = f"{HEADER}Length: {len(text)}\r\n\r\n{text}"
                conn.sendall(response.encode())
                print(f"[TXTP] Replied with {len(text)} bytes.")

def send_request(host: str, port: int):
    """
    Send a TXTP request to a server and print the response.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect((host, port))
        request = f"{HEADER}Request: text\r\n\r\n"
        client.sendall(request.encode())
        data = client.recv(4096)
        print("[TXTP] Received:\n")
        print(data.decode())
