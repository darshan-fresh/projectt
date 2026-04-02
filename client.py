"""
client.py — UDP Packet Sender
Sends packets with packet_id and timestamp to the server.
"""

import socket
import time
import argparse

def run_client(host="127.0.0.1", port=9999, interval=0.5):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packet_id = 0

    print(f"[CLIENT] Starting. Sending to {host}:{port} every {interval}s")

    try:
        while True:
            packet_id += 1
            message = f"{packet_id},{time.time()}"
            client.sendto(message.encode(), (host, port))
            print(f"[CLIENT] Sent packet #{packet_id}")
            time.sleep(interval)
    except KeyboardInterrupt:
        print(f"\n[CLIENT] Stopped. Total packets sent: {packet_id}")
    finally:
        client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Client — Packet Sender")
    parser.add_argument("--host", default="127.0.0.1", help="Server IP address")
    parser.add_argument("--port", type=int, default=9999, help="Server port")
    parser.add_argument("--interval", type=float, default=0.5, help="Send interval in seconds")
    args = parser.parse_args()

    run_client(args.host, args.port, args.interval)
