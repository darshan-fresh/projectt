"""
dashboard.py — Live Network Metrics Dashboard
Reads data.json every second and plots latency, jitter, and packet loss
in a styled real-time window.
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
import json
import time
import argparse
import os

# ── Style ───────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0d1117",
    "axes.facecolor":    "#161b22",
    "axes.edgecolor":    "#30363d",
    "axes.labelcolor":   "#8b949e",
    "axes.titlecolor":   "#e6edf3",
    "axes.grid":         True,
    "grid.color":        "#21262d",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.6,
    "xtick.color":       "#8b949e",
    "ytick.color":       "#8b949e",
    "text.color":        "#e6edf3",
    "font.family":       "monospace",
})

LATENCY_COLOR = "#58a6ff"
JITTER_COLOR  = "#3fb950"
LOSS_COLOR    = "#f85149"
FILL_ALPHA    = 0.15


def load_data(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def run_dashboard(data_file="data.json", refresh=1.0):
    print(f"[DASHBOARD] Watching {data_file} — refresh every {refresh}s")
    print("[DASHBOARD] Close the window or press Ctrl+C to quit.\n")

    plt.ion()
    fig = plt.figure(figsize=(13, 8), facecolor="#0d1117")
    fig.suptitle("  UDP Real-Time Network Metrics", fontsize=16,
                 fontweight="bold", color="#e6edf3", x=0.04, ha="left")

    gs = gridspec.GridSpec(2, 2, figure=fig,
                           hspace=0.55, wspace=0.35,
                           top=0.88, bottom=0.09,
                           left=0.07, right=0.97)

    ax_lat  = fig.add_subplot(gs[0, 0])   # Latency (line)
    ax_jit  = fig.add_subplot(gs[0, 1])   # Jitter  (line)
    ax_loss = fig.add_subplot(gs[1, 0])   # Packet Loss gauge (bar)
    ax_stat = fig.add_subplot(gs[1, 1])   # Stats text panel

    ax_stat.axis("off")

    try:
        while True:
            data = load_data(data_file)

            if data is None:
                plt.pause(refresh)
                continue

            latencies = data.get("latency", [])
            jitters   = data.get("jitter",  [])
            loss      = data.get("loss",    0.0)
            received  = data.get("received", 0)
            sent      = data.get("sent",     0)

            x_lat = list(range(len(latencies)))
            x_jit = list(range(len(jitters)))

            # ── Latency plot ─────────────────────────────────
            ax_lat.cla()
            if latencies:
                ax_lat.plot(x_lat, latencies, color=LATENCY_COLOR, linewidth=1.8, zorder=3)
                ax_lat.fill_between(x_lat, latencies, alpha=FILL_ALPHA, color=LATENCY_COLOR)
                avg = sum(latencies) / len(latencies)
                ax_lat.axhline(avg, color=LATENCY_COLOR, linewidth=0.8,
                               linestyle=":", alpha=0.7, label=f"avg {avg:.2f} ms")
                ax_lat.legend(fontsize=8, loc="upper right",
                              framealpha=0.2, labelcolor=LATENCY_COLOR)
            ax_lat.set_title("Latency", fontsize=11, pad=8)
            ax_lat.set_ylabel("ms", fontsize=9)
            ax_lat.set_xlabel("packets", fontsize=9)

            # ── Jitter plot ──────────────────────────────────
            ax_jit.cla()
            if jitters:
                ax_jit.plot(x_jit, jitters, color=JITTER_COLOR, linewidth=1.8, zorder=3)
                ax_jit.fill_between(x_jit, jitters, alpha=FILL_ALPHA, color=JITTER_COLOR)
                avg_j = sum(jitters) / len(jitters)
                ax_jit.axhline(avg_j, color=JITTER_COLOR, linewidth=0.8,
                               linestyle=":", alpha=0.7, label=f"avg {avg_j:.2f} ms")
                ax_jit.legend(fontsize=8, loc="upper right",
                              framealpha=0.2, labelcolor=JITTER_COLOR)
            ax_jit.set_title("Jitter", fontsize=11, pad=8)
            ax_jit.set_ylabel("ms", fontsize=9)
            ax_jit.set_xlabel("packets", fontsize=9)

            # ── Packet loss bar ──────────────────────────────
            ax_loss.cla()
            clamped = min(loss, 100.0)
            bar_color = (
                "#3fb950" if clamped < 10 else
                "#d29922" if clamped < 30 else
                "#f85149"
            )
            ax_loss.barh(["Loss"], [clamped],   color=bar_color,  height=0.4, zorder=3)
            ax_loss.barh(["Loss"], [100 - clamped], left=[clamped],
                         color="#21262d", height=0.4, zorder=2)
            ax_loss.set_xlim(0, 100)
            ax_loss.set_title("Packet Loss", fontsize=11, pad=8)
            ax_loss.set_xlabel("percent (%)", fontsize=9)
            ax_loss.text(clamped + 1.5, 0, f"{clamped:.1f}%",
                         va="center", fontsize=13, fontweight="bold",
                         color=bar_color)

            # ── Stats text panel ─────────────────────────────
            ax_stat.cla()
            ax_stat.axis("off")

            lines = [
                ("Packets Sent",     f"{sent}"),
                ("Packets Received", f"{received}"),
                ("Packet Loss",      f"{loss:.1f} %"),
            ]
            if latencies:
                lines += [
                    ("Latency  — cur", f"{latencies[-1]:.3f} ms"),
                    ("Latency  — avg", f"{sum(latencies)/len(latencies):.3f} ms"),
                    ("Latency  — max", f"{max(latencies):.3f} ms"),
                ]
            if jitters:
                lines += [
                    ("Jitter   — cur", f"{jitters[-1]:.3f} ms"),
                    ("Jitter   — avg", f"{sum(jitters)/len(jitters):.3f} ms"),
                ]

            y = 0.97
            ax_stat.text(0.0, y, "LIVE STATS", fontsize=10, fontweight="bold",
                         color="#e6edf3", transform=ax_stat.transAxes)
            y -= 0.10
            for label, value in lines:
                ax_stat.text(0.02, y, label, fontsize=9, color="#8b949e",
                             transform=ax_stat.transAxes)
                ax_stat.text(0.98, y, value, fontsize=9, color="#e6edf3",
                             ha="right", transform=ax_stat.transAxes, fontweight="bold")
                y -= 0.09

            # Timestamp
            ts = time.strftime("%H:%M:%S")
            fig.text(0.97, 0.97, f"updated {ts}", ha="right", va="top",
                     fontsize=8, color="#484f58")

            plt.pause(refresh)

    except KeyboardInterrupt:
        print("\n[DASHBOARD] Closed.")
    finally:
        plt.ioff()
        plt.close("all")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UDP Network Metrics Dashboard")
    parser.add_argument("--data-file", default="data.json", help="JSON file to read")
    parser.add_argument("--refresh",   type=float, default=1.0,
                        help="Refresh interval in seconds")
    args = parser.parse_args()

    run_dashboard(args.data_file, args.refresh)