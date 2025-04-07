import matplotlib.pyplot as plt
import os






filename = "src2_cubic_rtt_324ms.txt"  # <<< Edit this for your target file
flow_label = "TCP Flow 2 (src2 → rcv2)"
time_limit = 2000  # Display up to this time (in seconds)




def extract_info(filename):
    base = os.path.basename(filename).replace(".txt", "")
    parts = base.split("_")
    if len(parts) >= 4:
        _, algo, mode, rtt = parts
        return algo.upper(), mode.capitalize(), rtt
    return "UNKNOWN", "Unknown", "??ms"





algo, mode, rtt = extract_info(filename)
# === Parse iperf3 output ===
time = []
throughput = []

with open(filename, "r") as file:
    for line in file:
        if "sec" in line and "Mbits/sec" in line and "[" in line:
            parts = line.split()
            try:
                interval = parts[2]
                start_time = float(interval.split("-")[0])
                rate = float(parts[6])  # Mbits/sec
                if start_time <= time_limit:
                    time.append(start_time)
                    throughput.append(rate)
            except:
                continue

# === Plot ===
plt.figure(figsize=(12, 4))  # Wide view
plt.plot(time, throughput, label=flow_label, color='green', linewidth=1)
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Throughput (Mbits/sec)", fontsize=12)
plt.title(f"{algo} - Throughput vs Time ({mode}, RTT={rtt})", fontsize=14, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()
# === Save output ===
save_name = f"{algo.lower()}_singleflow_{mode.lower()}_{rtt}_first{time_limit}s.png"
plt.savefig(save_name, dpi=300)
plt.show()
