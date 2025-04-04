import matplotlib.pyplot as plt

# === Your log files ===
h1_file = "h1_bbr_162ms.txt"
h2_file = "h2_bbr_162ms.txt"

# === Function to parse iperf3 throughput logs ===
def parse_iperf3(filename):
    time = []
    throughput = []
    with open(filename, "r") as file:
        for line in file:
            if "sec" in line and "Mbits/sec" in line and "[" in line:
                parts = line.split()
                try:
                    interval = parts[2]  # e.g., 5.00-6.00
                    start_time = float(interval.split("-")[0])
                    rate = float(parts[6])  # Mbits/sec
                    time.append(start_time)
                    throughput.append(rate)
                except:
                    continue
    return time, throughput

# === Extract data ===
t1, tp1 = parse_iperf3(h1_file)
t2, tp2 = parse_iperf3(h2_file)

# === Plot setup ===
plt.figure(figsize=(10, 5))

# Smoother line styles (no markers)
plt.plot(t1, tp1, label='TCP Flow 1', color='purple', linewidth=1)
plt.plot(t2, tp2, label='TCP Flow 2', color='teal', linewidth=1)

plt.title("Change in Throughput (Mbps) vs Time for Two TCP Flows", fontsize=14, fontweight='bold')
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Throughput (Mbps)", fontsize=12)

# Optional: axis limits for a tighter range
plt.ylim(bottom=0)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11)
plt.tight_layout()

# Save and show
plt.savefig("throughput_comparison_bbr_162ms_clean.png", dpi=300)
plt.show()
