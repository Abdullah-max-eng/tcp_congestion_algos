import matplotlib.pyplot as plt

# === Edit these to match your file names ===
h1_file = "h1_bbr_162ms.txt"
h2_file = "h2_bbr_162ms.txt"

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

# === Plot setup ===
plt.figure(figsize=(12, 6))
plt.plot(t1, cwnd1, label="TCP Flow 1 (h1 → r1)", color='blue',
         linewidth=1, marker='o', markersize=4, markerfacecolor='none', alpha=0.7, linestyle='-')
plt.plot(t2, cwnd2, label="TCP Flow 2 (h2 → r2)", color='orange',
         linewidth=1, marker='s', markersize=4, markerfacecolor='none', alpha=0.7, linestyle='-')

plt.title("CWND vs Time for Two TCP Flows (BBR - 162ms)", fontsize=14, fontweight='bold')
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Congestion Window (packets)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.3)
plt.legend()
plt.tight_layout()

# Set axis limits with a little headroom
plt.xlim(0, max(max(t1, default=0), max(t2, default=0)) + 50)
plt.ylim(0, max(max(cwnd1, default=0), max(cwnd2, default=0)) + 500)

plt.savefig("cwnd_bbr_162ms_clearer.png", dpi=300)
plt.show()
