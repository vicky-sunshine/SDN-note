from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.util import dumpNodeConnections
from mininet.link import TCLink
from mininet.log import setLogLevel
from mininet.cli import CLI

class MyTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        # core switch
        core_sw_1 = self.addSwitch('s1001')
        core_sw_2 = self.addSwitch('s1002')
        core_sw_3 = self.addSwitch('s1003')
        core_sw_4 = self.addSwitch('s1004')

        # core switch
        for i in range(1, 5, 1):  # 1~4
            left_ag_sw = self.addSwitch('s200%s' % (2*i-1))
            right_ag_sw = self.addSwitch('s200%s' % (2*i))
            self.addLink(core_sw_1, left_ag_sw, bw=1000, loss=2)
            self.addLink(core_sw_2, left_ag_sw, bw=1000, loss=2)
            self.addLink(core_sw_3, right_ag_sw, bw=1000, loss=2)
            self.addLink(core_sw_4, right_ag_sw, bw=1000, loss=2)
            self.pod_generate(left_ag_sw, right_ag_sw, i-1)  # pod_index: 0~3

    def pod_generate(self, left_ag_sw, right_ag_sw, pod_index):
        # edge switch
        left_edge_sw = self.addSwitch('s300%s' % (2*pod_index+1))
        right_edge_sw = self.addSwitch('s300%s' % (2*pod_index+2))

        # host
        h1 = self.addHost('h%s1' % pod_index)
        h2 = self.addHost('h%s2' % pod_index)
        h3 = self.addHost('h%s3' % pod_index)
        h4 = self.addHost('h%s4' % pod_index)

        # ag -> edge
        self.addLink(left_ag_sw, left_edge_sw, bw=100)
        self.addLink(left_ag_sw, right_edge_sw, bw=100)
        self.addLink(right_ag_sw, left_edge_sw, bw=100)
        self.addLink(right_ag_sw, right_edge_sw, bw=100)

        # edge -> host
        self.addLink(left_edge_sw, h1, bw=100)
        self.addLink(left_edge_sw, h2, bw=100)
        self.addLink(right_edge_sw, h3, bw=100)
        self.addLink(right_edge_sw, h4, bw=100)


def test():
    topo = MyTopo()
    net = Mininet(topo=topo,
                  link=TCLink,
                  controller=None)
    net.addController('c0',
                      controller=RemoteController,
                      ip='127.0.0.1')
    net.start()

    print "Dumping host Connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    h01, h02, h31 = net.get('h01', 'h02', 'h31')

    # server, run in another thread in backround
    h02.popen("iperf -s -u -i 1")
    h31.popen("iperf -s -u -i 1")

    # client
    # `-u` generate udp traffic
    # `-t 10 `for 10 seconds
    # `-i 1` show info per second
    # `-b 100m` 100 Mbps bandwidth
    print "h01 connencting to h02"
    h01.cmdPrint("iperf -c " + h02.IP() + " -u -t 10 -i 1 -b 100m")
    print "h01 connencting to h31"
    h01.cmdPrint("iperf -c " + h31.IP() + " -u -t 10 -i 1 -b 100m")
    # CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    test()


topos = {'mytopo': (lambda: MyTopo())}
# sudo mn --custom mininet-script/fat_tree.py --topo mytopo --link=tc
