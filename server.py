"""
server.py — UDP Server + Metrics Engine
Receives packets, calculates latency/jitter/packet loss,
simulates packet loss, and writes results to data.json.
"""

import socket
import time
import json
import random
import argparse
import os

# ── Configuration ──────────────────────────────────────────────
LOSS_SIMULATION_RATE = 0.20   # 20% artificial packet loss
HISTORY_SIZE = 50             # How many data points to keep in JSON
# ───────────────────────────────────────────────────────────────

def run_server(host="0.0.0.0", port=9999, loss_rate=LOSS_SIMULATION_RATE, data_file="data.json"):
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))

    print(f"[SERVER] Listening on {host}:{port}")
    print(f"[SERVER] Simulated packet loss rate: {loss_rate * 100:.0f}%")
    print(f"[SERVER] Writing metrics to: {data_file}")

    latencies = []
    jitters = []
    received_packets = set()
    previous_latency = None
    highest_packet_id_seen = 0

    # Initialise an empty data.json so the dashboard doesn't crash on first read
    with open(data_file, "w") as f:
        json.dump({"latency": [], "jitter": [], "loss": 0.0, "received": 0, "sent": 0}, f)

    try:
        while True:
            data, addr = server.recvfrom(1024)

            # ── Simulate packet loss ────────────────────────────
            if random.random() < loss_rate:
                print(f"[SERVER] ⚠  Dropped packet (simulated loss)")
                continue

            recv_time = time.time()

            # ── Parse incoming packet ───────────────────────────
            try:
                packet_id_str, send_time_str = data.decode().split(",")
                packet_id = int(packet_id_str)
                send_time = float(send_time_str)
            except ValueError:
                print(f"[SERVER] ✗ Malformed packet from {addr}, skipping.")
                continue

            # ── Metrics calculation ─────────────────────────────
            latency = recv_time - send_time           # seconds
            latency_ms = latency * 1000               # milliseconds

            if previous_latency is not None:
                jitter_ms = abs(latency_ms - previous_latency)
            else:
                jitter_ms = 0.0

            previous_latency = latency_ms

            latencies.append(round(latency_ms, 4))
            jitters.append(round(jitter_ms, 4))
            received_packets.add(packet_id)

            highest_packet_id_seen = max(highest_packet_id_seen, packet_id)
            sent = highest_packet_id_seen
            received = len(received_packets)
            loss_pct = ((sent - received) / sent * 100) if sent > 0 else 0.0

            print(
                f"[SERVER] Pkt #{packet_id:>5} | "
                f"Latency: {latency_ms:>7.3f} ms | "
                f"Jitter: {jitter_ms:>7.3f} ms | "
                f"Loss: {loss_pct:>5.1f}%"
            )

            # ── Write metrics to JSON ───────────────────────────
            payload = {
                "latency":   latencies[-HISTORY_SIZE:],
                "jitter":    jitters[-HISTORY_SIZE:],
                "loss":      round(loss_pct, 2),
                "received":  received,
                "sent":      sent,
                "timestamp": recv_time
            }

            # Atomic-ish write: write to tmp then rename to avoid partial reads
            tmp_file = data_file + ".tmp"
            with open(tmp_file, "w") as f:
                json.dump(payload, f)
            os.replace(tmp_file, data_file)

    except KeyboardInterrupt:
        print(f"\n[SERVER] Stopped.")
        print(f"  Packets received : {len(received_packets)}")
        print(f"  Highest ID seen  : {highest_packet_id_seen}")
        if latencies:
            print(f"  Avg latency      : {sum(latencies)/len(latencies):.3f} ms")
            print(f"  Avg jitter       : {sum(jitters)/len(jitters):.3f} ms")
    finally:
        server.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Server — Metrics Engine")
    parser.add_argument("--host",      default="0.0.0.0",   help="Bind address")
    parser.add_argument("--port",      type=int, default=9999, help="Bind port")
    parser.add_argument("--loss-rate", type=float, default=LOSS_SIMULATION_RATE,
                        help="Simulated packet loss rate (0.0 – 1.0)")
    parser.add_argument("--data-file", default="data.json", help="Output JSON file path")
    args = parser.parse_args()

<<<<<<< HEAD
    run_server(args.host, args.port, args.loss_rate, args.data_file)
=======
    run_server(args.host, args.port, args.loss_rate, args.data_file)
>>>>>>> 96db6d3ae6d9fb35e27665e473743c89a1fbe45d
