import matplotlib.pyplot as plt

# === Your log files ===
h1_file = "h1_vegas_81ms.txt"
h2_file = "h2_vegas_81ms.txt"

# === Choose how many seconds to show on the X-axis ===
# Just edit this value as a string (e.g., "300" for 300 seconds)
max_seconds = "2000"
max_seconds = float(max_seconds)  # Convert to number

# === Function to parse iperf3 throughput logs ===
def parse_iperf3(filename, max_time):
    time = []
    throughput = []
    with open(filename, "r") as file:
        for line in file:
            if "sec" in line and "Mbits/sec" in line and "[" in line:
                parts = line.split()
                try:
                    interval = parts[2]  # e.g., 5.00-6.00
                    start_time = float(interval.split("-")[0])
                    if start_time > max_time:
                        continue
                    rate = float(parts[6])  # Mbits/sec
                    time.append(start_time)
                    throughput.append(rate)
                except:
                    continue
    return time, throughput

# === Extract data up to max_seconds ===
t1, tp1 = parse_iperf3(h1_file, max_seconds)
t2, tp2 = parse_iperf3(h2_file, max_seconds)

# === Plot setup ===
plt.figure(figsize=(10, 5))
plt.plot(t1, tp1, label='TCP Flow 1', color='purple', linewidth=1)
plt.plot(t2, tp2, label='TCP Flow 2', color='teal', linewidth=1)

plt.title(f"Change in Throughput (Mbps) vs Time (First {int(max_seconds)}s)", fontsize=14, fontweight='bold')
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Throughput (Mbps)", fontsize=12)
plt.ylim(bottom=0)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11)
plt.tight_layout()

# Save and show
plt.savefig(f"throughput_comparison_vegas_{int(max_seconds)}s.png", dpi=300)
plt.show()
