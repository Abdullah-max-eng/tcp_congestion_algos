import matplotlib.pyplot as plt

# === Edit this for the file you want to plot ===
filename = "h2_bbr_162ms.txt"
flow_label = "TCP Flow 1 (h1 → r1)"

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




# === Plot the data ===
plt.figure(figsize=(10, 5))





# Styled line: thin, dashed, green
plt.plot(time, throughput, label=flow_label, color='green', linestyle='-', linewidth=1, marker='.')
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Throughput (Mbits/sec)", fontsize=12)
plt.title(f"Throughput vs Time: {filename}", fontsize=14, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()

# Save the plot
save_name = filename.replace(".txt", ".png")
plt.savefig(save_name, dpi=300)

# Show the plot
plt.show()
