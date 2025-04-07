from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.log import setLogLevel
from time import sleep
import os

# === CONFIGURATION ===
DURATION = 2000
DELAY_SECOND_FLOW = 250
FAIRNESS_DURATION = 1000

# === SELECT ALGORITHMS ===
ALGORITHMS = [
    # 'reno',
    # 'cubic',
    #  'bbr',
       'vegas'
]

# === SELECT BACKBONE DELAYS (in ms) ===
DELAYS = [
    21,     # RTT = 42ms
    # 81,    # RTT = 162ms
    # 162    # RTT = 324ms
]

# === Topology Definition ===
class DumbbellTopo(Topo):
    def __init__(self, delay_backbone=21, **kwargs):
        super().__init__(**kwargs)
        # Hosts
        src1 = self.addHost('src1')
        src2 = self.addHost('src2')
        rcv1 = self.addHost('rcv1')
        rcv2 = self.addHost('rcv2')

        # Routers/Switches
        ar1 = self.addSwitch('ar1')
        ar2 = self.addSwitch('ar2')
        bb1 = self.addSwitch('bb1')
        bb2 = self.addSwitch('bb2')

        # Link parameters
        backbone_bw = 82
        access_bw = 21
        edge_bw = 80
        buffer_backbone = int(0.2 * backbone_bw * delay_backbone * 2)
        buffer_access = int(0.2 * access_bw * delay_backbone * 2)

        # Link setup
        self.addLink(src1, ar1, bw=edge_bw, max_queue_size=buffer_access)
        self.addLink(src2, ar1, bw=edge_bw, max_queue_size=buffer_access)
        self.addLink(ar1, bb1, bw=access_bw, max_queue_size=buffer_access)
        self.addLink(bb1, bb2, bw=backbone_bw, delay=f'{delay_backbone}ms', max_queue_size=buffer_backbone)
        self.addLink(bb2, ar2, bw=access_bw, max_queue_size=buffer_access)
        self.addLink(ar2, rcv1, bw=edge_bw, max_queue_size=buffer_access)
        self.addLink(ar2, rcv2, bw=edge_bw, max_queue_size=buffer_access)

# === Set TCP Congestion Control ===
def set_congestion_algorithm(algo):
    os.system(f"sysctl -w net.ipv4.tcp_congestion_control={algo}")
    current = os.popen("sysctl -n net.ipv4.tcp_congestion_control").read().strip()
    print(f"Set congestion control algorithm: {current}")




# === Experiment Runner ===
def run_experiment(duration, delay_ms, algorithm, fairness=False):
    print(f"\n=== Running {'Fairness' if fairness else 'Regular'} test with {algorithm.upper()}, RTT={delay_ms*2}ms ===")
    set_congestion_algorithm(algorithm)

    topo = DumbbellTopo(delay_backbone=delay_ms)
    net = Mininet(topo=topo, link=TCLink)
    net.start()

    src1, src2 = net.get('src1'), net.get('src2')
    rcv1, rcv2 = net.get('rcv1'), net.get('rcv2')

    # Output file name
    mode = "fairness" if fairness else "rtt"
    suffix = f"{algorithm}_{mode}_{delay_ms * 2}ms.txt"

    print("Starting iperf3 servers...")
    rcv1.cmd('iperf3 -s -p 5201 &')
    rcv2.cmd('iperf3 -s -p 5202 &')
    sleep(1)

    print("Starting Flow 1 (src1 → rcv1)...")
    src1.cmd(f'iperf3 -c {rcv1.IP()} -p 5201 -t {duration} -i 1 > src1_{suffix} &')

    if fairness:
        print("Starting Flow 2 (src2 → rcv2) immediately...")
        src2.cmd(f'iperf3 -c {rcv2.IP()} -p 5202 -t {duration} -i 1 > src2_{suffix} &')
        print(f"Waiting {duration}s for fairness test to complete...")
        sleep(duration)
    else:
        print(f"Waiting {DELAY_SECOND_FLOW}s before starting Flow 2...")
        sleep(DELAY_SECOND_FLOW)
        remaining = duration - DELAY_SECOND_FLOW
        print(f"Starting Flow 2 (src2 → rcv2, duration: {remaining}s)...")
        src2.cmd(f'iperf3 -c {rcv2.IP()} -p 5202 -t {remaining} -i 1 > src2_{suffix} &')
        print(f"Waiting {duration}s for full test to complete...")
        sleep(duration)

    print(f"Test complete. Output saved as src1_{suffix} and src2_{suffix}")
    net.stop()

# === Main ===
def main():
    setLogLevel('info')
    print("Running experiments for uncommented algorithms and delays...")

    for algorithm in ALGORITHMS:
        for delay in DELAYS:
            run_experiment(DURATION, delay, algorithm, fairness=False)
            run_experiment(FAIRNESS_DURATION, delay, algorithm, fairness=True)

    print("\nAll experiments completed.")

if __name__ == '__main__':
    main()
