from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel

class DumbbellTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        r1 = self.addHost('r1')
        r2 = self.addHost('r2')
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(s1, r1, cls=TCLink, bw=10, delay='162ms')
        self.addLink(s2, r2, cls=TCLink, bw=10, delay='162ms')
        self.addLink(r1, r2, cls=TCLink, bw=10, delay='162ms')

def run():
    topo = DumbbellTopo()
    net = Mininet(topo=topo, link=TCLink)
    net.start()
    print("Running CLI...")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
