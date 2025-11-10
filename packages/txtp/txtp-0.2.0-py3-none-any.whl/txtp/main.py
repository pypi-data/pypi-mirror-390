import socket

def run_server(bind_ip, port, text):
    print(f"[+] Binding to {bind_ip}:{port}")
    s = socket.socket(socket.AF_INET6 if ":" in bind_ip else socket.AF_INET, socket.SOCK_STREAM)
    s.bind((bind_ip, port))
    s.listen(1)
    print("[+] Waiting for connection...")

    conn, addr = s.accept()
    print(f"[+] Connected by {addr}")
    conn.sendall(text.encode())
    print(f"[+] Sent: {text}")
    conn.close()
    s.close()
    print("[+] Connection closed.")
