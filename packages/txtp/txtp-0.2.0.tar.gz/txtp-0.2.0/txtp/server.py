import socket
import threading
from .protocol import build_message

def start_server(host='0.0.0.0', port=8080, reply_text="Hello from TXTP Server!"):
    def handle_client(conn, addr):
        print(f"[+] Connection from {addr}")
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        response = build_message(reply_text)
        conn.sendall(response)
        conn.close()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(f"[TXTP] Server listening on {host}:{port}")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\n[TXTP] Server shutting down.")
    finally:
        server.close()
