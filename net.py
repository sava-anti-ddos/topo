""" SAV-D reflection attack scene topology
                        
                        h2
                        |
                        r2
                        |
                        r3----h6
                        |
        r1--------------r6---------------r7----------------r8
        |               |                |                  |
        |               |                |                  |
       h1               r5               h4                 h5
                        |
                        r4
                        |
                        h3
                      
"""

from mininet.net import Mininet
from mininet.node import Node
from mininet.topo import Topo
import os

TOPO_TOTAL_HOSTS = 6
TOPO_TOTAL_ROUTERS = 8
CONF_PREFIX = ''

class ReflectionAttackTopo(Topo):

    def build(self, **_opts):
        # define all hosts we need, h[0] is not used
        hosts = [0] * (TOPO_TOTAL_HOSTS+1)
        for i in range(1, TOPO_TOTAL_HOSTS+1):
            hosts[i] = self.addHost('h{}'.format(i))

        # define all routers we need, r[0] is not used
        routers = [0] * (TOPO_TOTAL_ROUTERS+1)
        for i in range(1, TOPO_TOTAL_ROUTERS+1):
            routers[i] = self.addHost('r{}'.format(i))

        # add link between host and router
        self.addLink(hosts[1], routers[1], intfName1 = 'h1-eth0', intfName2 = 'r1-eth0')
        self.addLink(hosts[2], routers[2], intfName1 = 'h2-eth0', intfName2 = 'r2-eth0')
        self.addLink(hosts[3], routers[4], intfName1 = 'h3-eth0', intfName2 = 'r4-eth0')
        self.addLink(hosts[4], routers[7], intfName1 = 'h4-eth0', intfName2 = 'r7-eth0')
        self.addLink(hosts[5], routers[8], intfName1 = 'h5-eth0', intfName2 = 'r8-eth0')
        self.addLink(hosts[6], routers[3], intfName1 = 'h6-eth0', intfName2 = 'r3-eth2')

        # add link between routers
        self.addLink(routers[1], routers[6], intfName1 = 'r1-eth1', intfName2 = 'r6-eth2')
        self.addLink(routers[2], routers[3], intfName1 = 'r2-eth1', intfName2 = 'r3-eth0')
        self.addLink(routers[3], routers[6], intfName1 = 'r3-eth1', intfName2 = 'r6-eth0')
        self.addLink(routers[4], routers[5], intfName1 = 'r4-eth1', intfName2 = 'r5-eth0')
        self.addLink(routers[5], routers[6], intfName1 = 'r5-eth1', intfName2 = 'r6-eth1')
        self.addLink(routers[6], routers[7], intfName1 = 'r6-eth3', intfName2 = 'r7-eth1')
        self.addLink(routers[7], routers[8], intfName1 = 'r7-eth2', intfName2 = 'r8-eth1')

class ReflectionAttackNet(Mininet):
    def __init__(self):
        super(ReflectionAttackNet, self).__init__(controller=None, 
                                topo = ReflectionAttackTopo(), autoSetMacs=True)

        self.r = [0] * (TOPO_TOTAL_ROUTERS+1)
        for i in range(1, TOPO_TOTAL_ROUTERS+1):
            self.r[i] = self.get('r{}'.format(i))
        self.h = [0] * (TOPO_TOTAL_HOSTS+1)
        for i in range(1, TOPO_TOTAL_HOSTS+1):
            self.h[i] = self.get('h{}'.format(i))
    
        self.bgpNodes = [1, 6, 7, 8]
        self.ospfNodes = [2, 3, 4, 5, 6]
        # chmod 777 -R CONF_PREFIX to allow quagga create log,pid,socket files
        os.system('sudo chmod 777 -R {}'.format(CONF_PREFIX))
    
    def start(self):
        super(ReflectionAttackNet, self).start()
        # configure IP addresses
        self.config_ip()
        # enable IP forwarding
        for i in range(1, TOPO_TOTAL_ROUTERS+1):
            self.r[i].cmd('sysctl net.ipv4.ip_forward=1')
            # disable rp_filter ?
            rp_disable(self.r[i])

        # set up host's default route
        self.h[1].setDefaultRoute('via 50.50.10.1')
        self.h[2].setDefaultRoute('via 20.20.30.1')
        self.h[3].setDefaultRoute('via 20.20.60.1')
        self.h[4].setDefaultRoute('via 30.30.10.1')
        self.h[5].setDefaultRoute('via 40.40.10.1')
        self.h[6].setDefaultRoute('via 20.20.70.1')

        # start sshd
        for host in self.h[1:]:
            host.cmd('/usr/sbin/sshd -D &')
        for router in self.r[1:]:
            router.cmd('/usr/sbin/sshd -D &')

        # start zebra
        for router in self.r[1:]:
            start_zebra(router)
        # start ospfd
        for i in self.ospfNodes:
            start_ospfd(self.r[i])
        # start bgpd
        for i in self.bgpNodes:
            start_bgpd(self.r[i])
    
    def stop(self):
        # stop zebra
        for router in self.r[1:]:
            stop_zebra(router)
        # stop bgpd
        for i in self.bgpNodes:
            stop_bgpd(self.r[i])
        # stop ospfd
        for i in self.ospfNodes:
            stop_ospfd(self.r[i])
        super(ReflectionAttackNet, self).stop()

    # provide a method to run a command on a node
    # this should be called after net.start()
    def cmd(self, node_name, cmd):
        return self.get(node_name).cmd(cmd)

    def config_ip(self):
        # set up routers IP addresses
        self.r[1].setIP('50.50.10.1/24', intf='r1-eth0')
        self.r[1].setIP('50.50.0.1/24', intf='r1-eth1')
        self.r[2].setIP('20.20.30.1/24', intf='r2-eth0')
        self.r[2].setIP('20.20.20.2/24', intf='r2-eth1')
        self.r[3].setIP('20.20.20.1/24', intf='r3-eth0')
        self.r[3].setIP('20.20.10.2/24', intf='r3-eth1')
        self.r[3].setIP('20.20.70.1/24', intf='r3-eth2')
        self.r[4].setIP('20.20.60.1/24', intf='r4-eth0')
        self.r[4].setIP('20.20.50.2/24', intf='r4-eth1')
        self.r[5].setIP('20.20.50.1/24', intf='r5-eth0')
        self.r[5].setIP('20.20.40.2/24', intf='r5-eth1')
        self.r[6].setIP('20.20.10.1/24', intf='r6-eth0')
        self.r[6].setIP('20.20.40.1/24', intf='r6-eth1')
        self.r[6].setIP('50.50.0.2/24', intf='r6-eth2')
        self.r[6].setIP('20.20.0.1/24', intf='r6-eth3')
        self.r[7].setIP('30.30.10.1/24', intf='r7-eth0')
        self.r[7].setIP('20.20.0.2/24', intf='r7-eth1')
        self.r[7].setIP('30.30.0.1/24', intf='r7-eth2')
        self.r[8].setIP('40.40.10.1/24', intf='r8-eth0')
        self.r[8].setIP('30.30.0.2/24', intf='r8-eth1')
        # set up hosts IP addresses
        self.h[1].setIP('50.50.10.10/24', intf='h1-eth0')
        self.h[2].setIP('20.20.30.10/24', intf='h2-eth0')
        self.h[3].setIP('20.20.60.10/24', intf='h3-eth0')
        self.h[4].setIP('30.30.10.10/24', intf='h4-eth0')
        self.h[5].setIP('40.40.10.10/24', intf='h5-eth0')
        self.h[6].setIP('20.20.70.10/24', intf='h6-eth0')

def start_zebra(r : Node):
    name = '{}'.format(r)
    dir='{}/{}/'.format(CONF_PREFIX, name)
    config = dir + 'zebra.conf'
    pid =  dir + 'zebra.pid'
    zsock=  dir + 'zserv.api'
    r.cmd('rm -f {}'.format(pid))    	# we need to delete the pid file
    r.cmd('/usr/sbin/zebra --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))

def stop_zebra(r : Node):
    name = '{}'.format(r)
    dir='{}/{}/'.format(CONF_PREFIX, name)
    pidfile =  dir + 'zebra.pid'
    f = open(pidfile)
    pid = int(f.readline())
    zsock=  dir + 'zserv.api'
    r.cmd('kill {}'.format(pid))
    r.cmd('rm {}'.format(pidfile))
    r.cmd('rm {}'.format(zsock))

def start_bgpd(r : Node):
    name = '{}'.format(r)
    dir='{}/{}/'.format(CONF_PREFIX, name)
    config = dir + 'bgpd.conf'
    zsock  = dir + 'zserv.api'
    pid    = dir + 'bgpd.pid'
    r.cmd('/usr/sbin/bgpd --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))
    
def stop_bgpd(r : Node):
    name = '{}'.format(r)
    dir='{}/{}/'.format(CONF_PREFIX, name)
    pidfile =  dir + 'bgpd.pid'
    f = open(pidfile)
    pid = int(f.readline())
    r.cmd('kill {}'.format(pid))
    r.cmd('rm {}'.format(pidfile))

def start_ospfd(r : Node):
    name = '{}'.format(r)
    dir='{}/{}/'.format(CONF_PREFIX, name)
    config = dir + 'ospfd.conf'
    zsock  = dir + 'zserv.api'
    pid    = dir + 'ospfd.pid'
    r.cmd('/usr/sbin/ospfd --daemon --config_file {} --pid_file {} --socket {}'.format(config, pid, zsock))

def stop_ospfd(r : Node):
    name = '{}'.format(r)
    dir='{}/{}/'.format(CONF_PREFIX, name)
    pidfile =  dir + 'ospfd.pid'
    f = open(pidfile)
    pid = int(f.readline())
    r.cmd('kill {}'.format(pid))
    r.cmd('rm {}'.format(pidfile))

def rp_disable(r : Node):
    ifacelist = r.intfList()
    for iface in ifacelist:
       if iface != 'lo': r.cmd('sysctl net.ipv4.conf.{}.rp_filter=0'.format(iface))