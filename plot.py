import matplotlib.pyplot as plt

# === Settings ===
filename = "h1_vegs_81ms.txt"
flow_label = "TCP Flow 1 (h1 → r1)"
time_limit = 2000  # <<< Edit this number to change how many seconds you want to display

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
                time.append(start_time)
                throughput.append(rate)
            except:
                continue

# === Apply time limit ===
filtered_time = []
filtered_throughput = []

for t, r in zip(time, throughput):
    if t <= time_limit:
        filtered_time.append(t)
        filtered_throughput.append(r)
    else:
        break

# === Plot the data ===
plt.figure(figsize=(12, 4))  # Wide view

plt.plot(filtered_time, filtered_throughput, label=flow_label, color='green', linewidth=1)

plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Throughput (Mbits/sec)", fontsize=12)
plt.title(f"Throughput vs Time (First {time_limit}s): {filename}", fontsize=14, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()

# Save and show
save_name = filename.replace(".txt", f"_first{time_limit}s.png")
plt.savefig(save_name, dpi=300)
plt.show()
