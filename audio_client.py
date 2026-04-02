"""
audio_client.py — Captures microphone and streams over UDP
Uses sounddevice (works on Python 3.13+)
"""

import socket
import sounddevice as sd
import numpy as np
import argparse

RATE     = 44100
CHANNELS = 1
CHUNK    = 1024

def run_audio_client(host="127.0.0.1", port=8888):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"[AUDIO CLIENT] Streaming mic to {host}:{port}")
    print("[AUDIO CLIENT] Speak into your microphone! Press Ctrl+C to stop.\n")

    def callback(indata, frames, time, status):
        sock.sendto(indata.tobytes(), (host, port))

    with sd.InputStream(samplerate=RATE, channels=CHANNELS,
                        dtype='int16', blocksize=CHUNK,
                        callback=callback):
        try:
            while True:
                sd.sleep(1000)
        except KeyboardInterrupt:
            print("\n[AUDIO CLIENT] Stopped.")

    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()
