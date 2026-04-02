"""
audio_server.py — Receives UDP audio and plays it in real time
Uses sounddevice (works on Python 3.13+)
"""

import socket
import sounddevice as sd
import numpy as np
import argparse

RATE     = 44100
CHANNELS = 1
CHUNK    = 1024

def run_audio_server(host="0.0.0.0", port=8888):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    print(f"[AUDIO SERVER] Listening on {host}:{port}")
    print("[AUDIO SERVER] Playing received audio... Press Ctrl+C to stop.\n")

    with sd.OutputStream(samplerate=RATE, channels=CHANNELS, dtype='int16') as stream:
        try:
            while True:
                data, _ = sock.recvfrom(CHUNK * 2)
                audio = np.frombuffer(data, dtype='int16')
                stream.write(audio)
        except KeyboardInterrupt:
            print("\n[AUDIO SERVER] Stopped.")

    sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8888)
    args = parser.parse_args()