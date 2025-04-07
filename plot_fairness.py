import matplotlib.pyplot as plt
import re
import os

# === Log files ===
flow1_file = "src1_reno_fairness_42ms.txt"
flow2_file = "src2_reno_fairness_42ms.txt"

# === Parameters ===
max_seconds = 2000
skip_initial_seconds = 5  # Ignore startup transients

# === Extract metadata from filename ===
def extract_info(filename):
    base = os.path.basename(filename).replace(".txt", "")
    parts = base.split("_")
    if len(parts) >= 4:
        _, algo, mode, rtt = parts
        return algo.upper(), mode.capitalize(), rtt
    return "UNKNOWN", "Unknown", "??ms"

# === Regex-based parser for iperf3 output ===
def parse_iperf3(filename, max_time, skip_initial=0):
    time = []
    throughput = []

    # Matches lines like: [ ID]   0.00-1.00 sec  1.23 MBytes  10.3 Mbits/sec
    pattern = re.compile(r'\[\s*\d+\]\s+(\d+\.\d+)-\d+\.\d+\s+sec\s+[\d\.]+\s+\w+Bytes\s+([\d\.]+)\s+Mbits/sec')

    with open(filename, 'r') as file:
        for line in file:
            match = pattern.search(line)
            if match:
                t = float(match.group(1))
                if t < skip_initial or t > max_seconds:
                    continue
                rate = float(match.group(2))
                time.append(t)
                throughput.append(rate)

    return time, throughput

# === Extract metadata for title and output ===
algo, mode, rtt = extract_info(flow1_file)

# === Parse logs ===
t1, tp1 = parse_iperf3(flow1_file, max_seconds, skip_initial=skip_initial_seconds)
t2, tp2 = parse_iperf3(flow2_file, max_seconds, skip_initial=skip_initial_seconds)

# === Plotting ===
plt.figure(figsize=(12, 6))

# Line plots instead of bars
plt.plot(t1, tp1, color='purple', linewidth=1, label='TCP Flow 1')
plt.plot(t2, tp2, color='seagreen', linewidth=1, label='TCP Flow 2')

# === Labels and Title ===
plt.title(f"{algo} - Throughput vs Time ({mode}, RTT={rtt})", fontsize=14, fontweight='bold')
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Throughput (Mbps)", fontsize=12)
plt.ylim(0, max(tp1 + tp2) + 10)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper right')
plt.tight_layout()

# Optional caption like the reference figure
plt.figtext(0.5, -0.04, f"Figure: Change in Throughput (Mbps) vs Time for two TCP flows using {algo} (RTT = {rtt})", wrap=True,
            horizontalalignment='center', fontsize=10, style='italic')

# === Save and show ===
output_filename = f"{algo.lower()}_lineplot_{mode.lower()}_{rtt}.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
plt.show()
