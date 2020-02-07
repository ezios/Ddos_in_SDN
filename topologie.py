#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node,Controller, OVSKernelSwitch, RemoteController
from mininet.log import setLogLevel, info
from mininet.cli import CLI
import time
class NetworkTopo(Topo):

    def build( self, **_opts ):
	    #creating two legacy switch
	#cls=OVSKernelSwitch
        s1, s2 = [ self.addSwitch( s,cls=OVSKernelSwitch ) for s in ( 's1', 's2' ) ]
	    #one Openflow switch
        s3 = self.addSwitch("s3")
	    #create six host ,and link them to the two legacy switch 3/switch
        client1  = self.addHost("client1",ip="10.0.0.1")
        client2  = self.addHost("client2",ip="10.0.0.2")
        dos_launch = self.addHost("dos_launch",ip="10.0.0.3")
    
        self.addLink(client1,s1)
        self.addLink(client2,s1)
        self.addLink(dos_launch,s1)
    
        server = self.addHost("server",ip="10.0.0.11")
        t_gen1     = self.addHost("t_gen1",ip="10.0.0.12")
        t_gen2     = self.addHost("t_gen2",ip="10.0.0.13")
    
        self.addLink(t_gen1,s2)
        self.addLink(t_gen2,s2)
        self.addLink(server,s2)
    
	#link legacy switches to Openflow switch
        self.addLink(s3,s1)
        self.addLink(s3,s2)

def run():
    #create remote cotroller , giving address and port
    c=RemoteController( 'c', ip="192.168.12.1", port=6633)
    topo = NetworkTopo()
    net = Mininet(topo=topo,controller=c,ipBase='10.0.0.0/8')
   # net.addController(c)
    net.start()
    net.pingAll()
    g1=     net.get("t_gen1")
    g2=     net.get("t_gen2")
    server= net.get('server')
    dos =   net.get("dos_launch")
    client = net.get("client1")
    
    #server.cmd("nohup python script/server.py > minilog/server.log &")
    server.cmd("nohup python -m SimpleHTTPServer 8888 >minilog/server.log &")
    print("[+] Web server is listenning")
    
    
    g1.cmd("nohup python script/gen1 > minilog/g1.log &")
    print("[+] traffic generator 1 is on")
    
    g2.cmd("nohup python script/gen2 > minilog/g2.log &")
    print("[+] traffic generator 2 on")

    client.cmd("nohup python3 script/client.py 10.0.0.11:8888 > minilog/client.log &")
    print("[+] client up")
    time.sleep(2)
    
    dos.cmd("nohup python3 script/httpflood.py > minilog/attacker.log &")
    print("[*] DOS attack launched")
    
    
        
    CLI(net) 
    net.stop   
if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
