import matplotlib.pyplot as plt

# === Your log files ===
h1_file = "h1_cubic_81ms.txt"
h2_file = "h2_cubic_81ms.txt"

def parse_iperf3(filename):
    time = []
    throughput = []
    with open(filename, "r") as file:
        for line in file:
            if "sec" in line and "Mbits/sec" in line and "[" in line:
                parts = line.split()
                try:
                    interval = parts[2]
                    start = float(interval.split("-")[0])
                    rate = float(parts[6])  # Mbits/sec
                    time.append(start)
                    throughput.append(rate)
                except:
                    continue
    return time, throughput

# === Extract throughput data ===
t1, tp1 = parse_iperf3(h1_file)
t2, tp2 = parse_iperf3(h2_file)

# === Plot setup ===
plt.figure(figsize=(10, 5))

# Styled plot lines (thinner, different styles/colors)
plt.plot(t1, tp1, label='TCP Flow 1 (h1 → r1)', color='darkorange', linestyle='-', linewidth=1, marker='^', markersize=4)
plt.plot(t2, tp2, label='TCP Flow 2 (h2 → r2)', color='dodgerblue', linestyle=':', linewidth=1, marker='v', markersize=4)

plt.title("Fairness: Throughput vs Time (cubic - 81ms Delay)", fontsize=14, fontweight='bold')
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Throughput (Mbits/sec)", fontsize=12)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(fontsize=11)
plt.tight_layout()

# Save and show
plt.savefig("fairness_cubic_81ms.png", dpi=300)
plt.show()
