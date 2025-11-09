HEADER_SIGNATURE = "TXTP/1.0"

def build_message(text: str) -> bytes:
    body = text.encode('utf-8')
    header = f"{HEADER_SIGNATURE}\nContent-Length: {len(body)}\n\n"
    return header.encode('utf-8') + body

def parse_message(data: bytes) -> str:
    try:
        header, body = data.split(b"\n\n", 1)
        if HEADER_SIGNATURE.encode() not in header:
            raise ValueError("Invalid TXTP header")
        return body.decode('utf-8')
    except Exception as e:
        return f"[TXTP ERROR] {e}"
