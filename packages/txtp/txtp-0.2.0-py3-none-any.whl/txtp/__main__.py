import argparse
from . import main

def cli():
    parser = argparse.ArgumentParser(description="TXT Protocol - Simple TCP text transfer")
    parser.add_argument("--bind", default="127.0.0.1", help="IP address to bind to (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Port number (default: 8080)")
    parser.add_argument("-t", "--text", required=True, help="Text to send")
    args = parser.parse_args()

    main.run_server(args.bind, args.port, args.text)

if __name__ == "__main__":
    cli()
