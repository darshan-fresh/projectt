"""
dashboard.py — Upgraded UDP Network Metrics Dashboard
- Better styled graphs with markers
- Packet loss history graph (new)
- Min / Max / Avg summary cards
- Live clock
"""

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import json
import time
import argparse

# ── Theme ───────────────────────────────────────────────────────
BG          = "#0d1117"
PANEL       = "#161b22"
BORDER      = "#30363d"
TEXT_DIM    = "#8b949e"
TEXT_BRIGHT = "#e6edf3"

LATENCY_C  = "#58a6ff"
JITTER_C   = "#3fb950"
LOSS_C     = "#f85149"
LOSS_OK_C  = "#3fb950"
LOSS_MID_C = "#d29922"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    PANEL,
    "axes.edgecolor":    BORDER,
    "axes.labelcolor":   TEXT_DIM,
    "axes.titlecolor":   TEXT_BRIGHT,
    "axes.titlesize":    11,
    "axes.titlepad":     10,
    "axes.grid":         True,
    "grid.color":        "#21262d",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.5,
    "xtick.color":       TEXT_DIM,
    "ytick.color":       TEXT_DIM,
    "xtick.labelsize":   8,
    "ytick.labelsize":   8,
    "text.color":        TEXT_BRIGHT,
    "font.family":       "monospace",
    "legend.framealpha": 0.15,
    "legend.fontsize":   8,
})

def load_data(path):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return None

def loss_color(pct):
    if pct < 10:  return LOSS_OK_C
    if pct < 30:  return LOSS_MID_C
    return LOSS_C

def draw_stat_card(ax, title, cur, mn, avg, mx, unit, color):
    ax.cla()
    ax.set_facecolor("#0d1117")
    for spine in ax.spines.values():
        spine.set_edgecolor(color)
        spine.set_linewidth(1.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.5, 0.88, title, ha="center", fontsize=9,
            color=color, fontweight="bold", transform=ax.transAxes)
    cur_str = f"{cur:.3f}" if cur is not None else "--"
    ax.text(0.5, 0.58, f"{cur_str} {unit}", ha="center", fontsize=15,
            color=TEXT_BRIGHT, fontweight="bold", transform=ax.transAxes)
    for x, label, val in [(0.18, "MIN", mn), (0.5, "AVG", avg), (0.82, "MAX", mx)]:
        val_str = f"{val:.3f}" if val is not None else "--"
        ax.text(x, 0.28, label, ha="center", fontsize=7,
                color=TEXT_DIM, transform=ax.transAxes)
        ax.text(x, 0.12, val_str, ha="center", fontsize=8,
                color=color, fontweight="bold", transform=ax.transAxes)

def run_dashboard(data_file="data.json", refresh=1.0):
    print(f"[DASHBOARD] Watching {data_file} — refresh {refresh}s")
    plt.ion()
    fig = plt.figure(figsize=(14, 9), facecolor=BG)

    gs = gridspec.GridSpec(3, 3, figure=fig,
                           hspace=0.60, wspace=0.38,
                           top=0.88, bottom=0.07,
                           left=0.06, right=0.97)

    ax_lat      = fig.add_subplot(gs[0, 0:2])
    ax_jit      = fig.add_subplot(gs[1, 0:2])
    ax_loss_bar = fig.add_subplot(gs[2, 0])
    ax_loss_his = fig.add_subplot(gs[2, 1])
    ax_card_lat = fig.add_subplot(gs[0, 2])
    ax_card_jit = fig.add_subplot(gs[1, 2])
    ax_card_pkt = fig.add_subplot(gs[2, 2])

    fig.text(0.04, 0.95, "UDP REAL-TIME NETWORK METRICS",
             fontsize=15, fontweight="bold", color=TEXT_BRIGHT, va="top")
    clock_txt = fig.text(0.97, 0.95, "", fontsize=9,
                         color=TEXT_DIM, ha="right", va="top")

    loss_history = []

    try:
        while True:
            clock_txt.set_text(time.strftime("%H:%M:%S  %d %b %Y"))
            data = load_data(data_file)
            if data is None:
                plt.pause(refresh)
                continue

            latencies = data.get("latency", [])
            jitters   = data.get("jitter",  [])
            loss      = data.get("loss",    0.0)
            received  = data.get("received", 0)
            sent      = data.get("sent",     0)
            lc        = loss_color(loss)

            loss_history.append(round(loss, 2))
            if len(loss_history) > 60:
                loss_history.pop(0)

            x_lat = list(range(len(latencies)))
            x_jit = list(range(len(jitters)))
            x_lh  = list(range(len(loss_history)))

            # Latency
            ax_lat.cla()
            if latencies:
                ax_lat.plot(x_lat, latencies, color=LATENCY_C, linewidth=2,
                            marker="o", markersize=3, zorder=3)
                ax_lat.fill_between(x_lat, latencies, alpha=0.18, color=LATENCY_C)
                avg_l = sum(latencies) / len(latencies)
                ax_lat.axhline(avg_l, color=LATENCY_C, linewidth=0.9,
                               linestyle=":", alpha=0.6, label=f"avg {avg_l:.3f} ms")
                ax_lat.legend(loc="upper right", labelcolor=LATENCY_C)
            ax_lat.set_title("▸  LATENCY", fontweight="bold")
            ax_lat.set_ylabel("ms", fontsize=8)
            ax_lat.set_xlabel("packets", fontsize=8)

            # Jitter
            ax_jit.cla()
            if jitters:
                ax_jit.plot(x_jit, jitters, color=JITTER_C, linewidth=2,
                            marker="o", markersize=3, zorder=3)
                ax_jit.fill_between(x_jit, jitters, alpha=0.18, color=JITTER_C)
                avg_j = sum(jitters) / len(jitters)
                ax_jit.axhline(avg_j, color=JITTER_C, linewidth=0.9,
                               linestyle=":", alpha=0.6, label=f"avg {avg_j:.3f} ms")
                ax_jit.legend(loc="upper right", labelcolor=JITTER_C)
            ax_jit.set_title("▸  JITTER", fontweight="bold")
            ax_jit.set_ylabel("ms", fontsize=8)
            ax_jit.set_xlabel("packets", fontsize=8)

            # Loss bar
            ax_loss_bar.cla()
            clamped = min(loss, 100.0)
            ax_loss_bar.barh([""], [clamped], color=lc, height=0.5, zorder=3)
            ax_loss_bar.barh([""], [100 - clamped], left=[clamped],
                             color="#21262d", height=0.5, zorder=2)
            ax_loss_bar.set_xlim(0, 100)
            ax_loss_bar.set_title("▸  PACKET LOSS", fontweight="bold")
            ax_loss_bar.set_xlabel("percent (%)", fontsize=8)
            ax_loss_bar.text(min(clamped + 2, 90), 0, f"{clamped:.1f}%",
                             va="center", fontsize=13, fontweight="bold", color=lc)

            # Loss history
            ax_loss_his.cla()
            if loss_history:
                ax_loss_his.plot(x_lh, loss_history, color=lc, linewidth=1.8, zorder=3)
                ax_loss_his.fill_between(x_lh, loss_history, alpha=0.18, color=lc)
                ax_loss_his.set_ylim(0, 105)
            ax_loss_his.set_title("▸  LOSS HISTORY", fontweight="bold")
            ax_loss_his.set_ylabel("%", fontsize=8)
            ax_loss_his.set_xlabel("samples", fontsize=8)

            # Cards
            if latencies:
                draw_stat_card(ax_card_lat, "LATENCY",
                               cur=latencies[-1], mn=min(latencies),
                               avg=sum(latencies)/len(latencies),
                               mx=max(latencies), unit="ms", color=LATENCY_C)
            if jitters:
                draw_stat_card(ax_card_jit, "JITTER",
                               cur=jitters[-1], mn=min(jitters),
                               avg=sum(jitters)/len(jitters),
                               mx=max(jitters), unit="ms", color=JITTER_C)

            # Packet card
            ax_card_pkt.cla()
            ax_card_pkt.set_facecolor("#0d1117")
            for spine in ax_card_pkt.spines.values():
                spine.set_edgecolor(lc)
                spine.set_linewidth(1.5)
            ax_card_pkt.set_xticks([])
            ax_card_pkt.set_yticks([])
            ax_card_pkt.text(0.5, 0.88, "PACKETS", ha="center", fontsize=9,
                             color=lc, fontweight="bold", transform=ax_card_pkt.transAxes)
            ax_card_pkt.text(0.5, 0.62, f"{loss:.1f}% loss", ha="center",
                             fontsize=14, color=TEXT_BRIGHT, fontweight="bold",
                             transform=ax_card_pkt.transAxes)
            for x, label, val, c in [
                (0.25, "SENT",     str(sent),     TEXT_BRIGHT),
                (0.75, "RECEIVED", str(received), lc)
            ]:
                ax_card_pkt.text(x, 0.35, label, ha="center", fontsize=7,
                                 color=TEXT_DIM, transform=ax_card_pkt.transAxes)
                ax_card_pkt.text(x, 0.18, val, ha="center", fontsize=11,
                                 color=c, fontweight="bold",
                                 transform=ax_card_pkt.transAxes)

            plt.pause(refresh)

    except KeyboardInterrupt:
        print("\n[DASHBOARD] Closed.")
    finally:
        plt.ioff()
        plt.close("all")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upgraded UDP Dashboard")
    parser.add_argument("--data-file", default="data.json")
    parser.add_argument("--refresh",   type=float, default=1.0)
    args = parser.parse_args()
    run_dashboard(args.data_file, args.refresh)
