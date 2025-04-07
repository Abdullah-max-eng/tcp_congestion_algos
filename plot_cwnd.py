import matplotlib.pyplot as plt
import os

# === Edit these to match your file names ===
h1_file = "src1_vegas_rtt_42ms.txt"
h2_file = "src2_vegas_rtt_42ms.txt"

# === Extract info from file name ===
def extract_plot_info(filename):
    base = os.path.basename(filename)
    parts = base.replace(".txt", "").split("_")
    if len(parts) >= 4:
        _, algo, mode, rtt = parts
        return algo.upper(), mode.capitalize(), rtt
    return "Unknown", "Unknown", "Unknown"

algo, mode, rtt = extract_plot_info(h1_file)

# === Function to extract time and CWND from iperf3 output ===
def parse_cwnd(filename):
    times = []
    cwnd_packets = []
    with open(filename, "r") as f:
        for line in f:
            if "sec" in line and "[" in line and ("KBytes" in line or "MBytes" in line):
                parts = line.split()
                try:
                    time_str = parts[2]
                    time = float(time_str.split('-')[0])

                    value = float(parts[4])
                    unit = parts[5]

                    if unit == "KBytes":
                        cwnd_kb = value
                    elif unit == "MBytes":
                        cwnd_kb = value * 1024
                    else:
                        continue

                    cwnd = cwnd_kb * 1024 / 1460  # Convert KB to packets
                    times.append(time)
                    cwnd_packets.append(cwnd)
                except:
                    continue
    return times, cwnd_packets

# === Parse each file ===
t1, cwnd1 = parse_cwnd(h1_file)
t2, cwnd2 = parse_cwnd(h2_file)

# === Shift Flow 2's start time by 250 seconds ===
t2 = [t + 250 for t in t2]

# === Plot setup ===
plt.figure(figsize=(12, 6))

# Use clean line plots (no markers)
plt.plot(t1, cwnd1, label="TCP Flow 1 (src1 → rcv1)", color='blue', linewidth=1)
plt.plot(t2, cwnd2, label="TCP Flow 2 (src2 → rcv2)", color='orange', linewidth=1)

# Title and labels
plt.title(f"{algo} - Congestion Window vs Time ({mode}, RTT={rtt})", fontsize=14, fontweight='bold')
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Congestion Window (packets)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.4)
plt.legend(loc='upper right')
plt.tight_layout()

# Axis limits
plt.xlim(0, max(max(t1, default=0), max(t2, default=0)) + 50)
plt.ylim(0, max(max(cwnd1, default=0), max(cwnd2, default=0)) + 500)

# Optional figure caption
plt.figtext(0.5, -0.04,
            f"Figure: Change in Congestion Window (packets) vs Time for two TCP flows using {algo} ({mode.lower()}, RTT = {rtt})",
            wrap=True, horizontalalignment='center', fontsize=10, style='italic')

# Save and show
plt.savefig(f"cwnd_{algo.lower()}_{mode.lower()}_{rtt}.png", dpi=300, bbox_inches='tight')
plt.show()
