#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.log import setLogLevel

import sys
import os
import time

#######################################################
# CONFIGURATION SECTION - EDIT THESE VALUES AS NEEDED #
#######################################################

# List of congestion control algorithms to test
# Uncomment/comment algorithms as needed
ALGORITHMS = [
    'reno',
    # 'cubic',
    # 'bbr',
    # 'vegas'
]

# List of backbone delays to test (in ms)
# These are one-way propagation delays as specified in the PDF
DELAYS = [
    21,     # Short delay (RTT = 42ms)
   # 81,     # Medium delay (RTT = 162ms)
   # 162     # Long delay (RTT = 324ms)
]

# Experiment durations (in seconds)
DURATION = 2000        # Duration for regular tests
FAIRNESS_DURATION = 1000  # Duration for fairness tests
DELAY_SECOND_FLOW = 250   # Delay before starting second flow in regular tests

#######################################################
# END OF CONFIGURATION SECTION                        #
#######################################################

def setup_tcp_probe():
    """Setup tcp_probe module to monitor congestion window"""
    os.system("rmmod tcp_probe 2>/dev/null; modprobe tcp_probe")
    os.system("echo 1 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable")
    return

def stop_tcp_probe():
    """Stop tcp_probe monitoring"""
    os.system("echo 0 > /sys/kernel/debug/tracing/events/tcp/tcp_probe/enable")
    os.system("rmmod tcp_probe")
    return

def set_tcp_congestion(cong_alg):
    """Set TCP congestion control algorithm"""
    os.system("sysctl -w net.ipv4.tcp_congestion_control=%s" % cong_alg)
    result = os.popen("sysctl -n net.ipv4.tcp_congestion_control").read().strip()
    print("TCP congestion control algorithm set to: %s" % result)
    return result





class DumbbellTopo(Topo):
    """Create a dumbbell topology as specified in the assignment"""
    def __init__(self, delay_backbone=21, **kwargs):
        Topo.__init__(self, **kwargs)
        
        # Network parameters directly from PDF
        backbone_bw = 82  # packets/ms
        access_bw = 21    # packets/ms (bottleneck)
        edge_bw = 80      # packets/ms
        
        # Calculate buffer sizes (20% of BDP)
        buffer_backbone = int(0.2 * backbone_bw * delay_backbone * 2)  # BDP = bw * RTT
        buffer_access = int(0.2 * access_bw * delay_backbone * 2)
        
        # Create network nodes
        # Routers (using switches in mininet)
        bb1 = self.addSwitch('bb1')  # Backbone Router 1
        bb2 = self.addSwitch('bb2')  # Backbone Router 2
        ar1 = self.addSwitch('ar1')  # Access Router 1
        ar2 = self.addSwitch('ar2')  # Access Router 2
        
        # Hosts
        src1 = self.addHost('src1')  # Source 1
        src2 = self.addHost('src2')  # Source 2
        rcv1 = self.addHost('rcv1')  # Receiver 1
        rcv2 = self.addHost('rcv2')  # Receiver 2
        
        # Add links - no extra delay except for backbone
        # Sources to Access Router 1
        self.addLink(src1, ar1, bw=edge_bw, max_queue_size=buffer_access)
        self.addLink(src2, ar1, bw=edge_bw, max_queue_size=buffer_access)
        
        # Access Router 1 to Backbone Router 1
        self.addLink(ar1, bb1, bw=access_bw, max_queue_size=buffer_access)
        
        # Backbone Router 1 to Backbone Router 2 (configurable delay)
        self.addLink(bb1, bb2, bw=backbone_bw, delay='%dms' % delay_backbone, 
                    max_queue_size=buffer_backbone)
        
        # Backbone Router 2 to Access Router 2
        self.addLink(bb2, ar2, bw=access_bw, max_queue_size=buffer_access)
        
        # Access Router 2 to Receivers
        self.addLink(ar2, rcv1, bw=edge_bw, max_queue_size=buffer_access)
        self.addLink(ar2, rcv2, bw=edge_bw, max_queue_size=buffer_access)








def run_experiment(net, cong_alg, delay_backbone, duration, delay_second_flow):
    """Run a TCP congestion control experiment"""
    # Set congestion control algorithm
    algorithm = set_tcp_congestion(cong_alg)
    
    # Create output directory if needed
    output_dir = 'results'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Determine output filename
    if delay_second_flow == 0:
        # This is a fairness test
        output_file = "%s/%s_fairness_%dms.txt" % (output_dir, algorithm, delay_backbone*2)
    else:
        # This is a regular test
        output_file = "%s/%s_rtt_%dms.txt" % (output_dir, algorithm, delay_backbone*2)
    
    print("\n========================================================")
    print("Starting experiment: %s, RTT=%dms, Duration=%ds" % 
          (algorithm, delay_backbone*2, duration))
    print("Output file: %s" % output_file)
    print("========================================================\n")
    
    # Start iperf servers on receivers
    print("Starting iperf servers on receivers")
    net['rcv1'].cmd('iperf -s -p 5001 > /dev/null &')
    net['rcv2'].cmd('iperf -s -p 5002 f> /dev/null &')
    time.sleep(1)  # Give servers time to start
    
    # Start TCP probe monitoring
    setup_tcp_probe()
    os.system("cat /sys/kernel/debug/tracing/trace_pipe > %s &" % output_file)
    monitoring_pid = int(os.popen("pgrep -f 'cat /sys/kernel/debug/tracing/trace_pipe'").read().strip())
    
    # Start first flow
    print("Starting first flow (Source #1 -> Receiver #1)")
    net['src1'].cmd('iperf -c %s -p 5001 -t %d -i 1 > /dev/null &' % 
                   (net["rcv1"].IP(), duration))
    
    # Start second flow
    if delay_second_flow > 0:
        # Wait before starting second flow
        print("Waiting %ds before starting second flow" % delay_second_flow)
        time.sleep(delay_second_flow)
        
        # Calculate remaining duration for second flow
        flow2_duration = duration - delay_second_flow
        print("Starting second flow (Source #2 -> Receiver #2)")
        net['src2'].cmd('iperf -c %s -p 5002 -t %d -i 1 > /dev/null &' % 
                       (net["rcv2"].IP(), flow2_duration))
    else:
        # Start second flow immediately (fairness test)
        print("Starting second flow (Source #2 -> Receiver #2) - Fairness test")
        net['src2'].cmd('iperf -c %s -p 5002 -t %d -i 1 > /dev/null &' % 
                       (net["rcv2"].IP(), duration))
    
    # Let the experiment run
    print("Experiment running for %ds..." % duration)
    print("(This will take a while - please be patient)")
    
    # Show progress updates every 5 minutes
    update_interval = 300  # 5 minutes
    for i in range(duration // update_interval):
        time.sleep(update_interval)
        remaining = duration - (i+1) * update_interval
        print("  %d seconds remaining..." % remaining)
    
    # Wait for any remaining time
    time.sleep(duration % update_interval)
    
    # Stop monitoring
    os.system("kill %d" % monitoring_pid)
    stop_tcp_probe()
    
    # Clean up iperf
    os.system("killall -9 iperf")
    
    print("\nExperiment complete. Results saved to %s" % output_file)

def run_regular_tests():
    """Run tests with delayed second flow for each algorithm and delay"""
    print("\n==== Running Regular Tests (Delayed Second Flow) ====")
    print("Testing algorithms: %s" % ALGORITHMS)
    print("Testing delays: %s ms" % DELAYS)
    print("Test duration: %d seconds" % DURATION)
    print("Second flow starts after: %d seconds" % DELAY_SECOND_FLOW)
    
    # Test each algorithm with each delay
    for algo in ALGORITHMS:
        for delay in DELAYS:
            # Create network
            topo = DumbbellTopo(delay_backbone=delay)
            net = Mininet(topo=topo, link=TCLink)
            net.start()
            
            # Run experiment
            run_experiment(net, algo, delay, DURATION, DELAY_SECOND_FLOW)
            
            # Clean up
            net.stop()
            os.system("mn -c > /dev/null 2>&1")
            print("Waiting 5 seconds before next test...")
            time.sleep(5)




def run_fairness_tests():
    """Run fairness tests (simultaneous flows) for each algorithm with all delays"""
    print("\n==== Running Fairness Tests (Simultaneous Flows) ====")
    print("Testing algorithms: %s" % ALGORITHMS)
    print("Testing delays: %s ms" % DELAYS)
    print("Test duration: %d seconds" % FAIRNESS_DURATION)
    
    # Test each algorithm with each delay
    for algo in ALGORITHMS:
        for delay in DELAYS:
            # Create network
            topo = DumbbellTopo(delay_backbone=delay)
            net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, controller=None)
            net.start()
            
            # Run fairness experiment (both flows start simultaneously)
            run_experiment(net, algo, delay, FAIRNESS_DURATION, 0)
            
            # Clean up
            net.stop()
            os.system("mn -c > /dev/null 2>&1")
            print("Waiting 5 seconds before next test...")
            time.sleep(5)











def main():
    """Main function to run experiments"""
    setLogLevel('info')
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'regular':
            run_regular_tests()
        elif sys.argv[1] == 'fairness':
            run_fairness_tests()
        else:
            print("Unknown option. Usage: %s [regular|fairness]" % sys.argv[0])
            print("  regular  - Run tests with delayed second flow")
            print("  fairness - Run tests with simultaneous flows")
    else:
        # No arguments provided - show menu
        print("\nTCP Congestion Control Experiment")
        print("=================================")
        print("Choose an option:")
        print("  1. Run regular tests (delayed second flow)")
        print("  2. Run fairness tests (simultaneous flows)")
        print("  3. Run both types of tests")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            run_regular_tests()
        elif choice == '2':
            run_fairness_tests()
        elif choice == '3':
            run_regular_tests()
            run_fairness_tests()
        else:
            print("Invalid choice. Exiting.")

if __name__ == '__main__':
    main()