#coding:utf-8

from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of
from pox.openflow.of_json import *
from pox.lib.recoco import Timer
import time
import json





log = core.getLogger()
temp = time.time()
table={}
stats={}
blacklist = []

def sendpacket(event, dst_port = of.OFPP_ALL):
	#ofp.in_port port par lequel le paquet est arrivé
	msg = of.ofp_packet_out(in_port = event.ofp.in_port)
	if event.ofp.buffer_id not in [-1,None]:
		msg.buffer_id = event.ofp.buffer_id
	else:
		if not event.ofp.data:
			return
		msg.data = event.ofp.data
	msg.actions.append(of.ofp_action_output(port = dst_port))
	event.connection.send(msg)
def switch(event):
	
	global table
	global temp
	global blacklist
	global stats

	packet = event.parsed
	#Ajout d'une entrée à la table de commutation
	table[packet.src] = event.port
	# essai de lecture du port de destination corespondant 
	#à la mac de destination
	dst_port = table.get(packet.dst)
	if str(packet.src) in blacklist:
		sendpacket(event,port = 0)
	#blacklist contenant les ports physiques à ignorer

	elif packet.dst.is_multicast:
		sendpacket(event,of.OFPP_FLOOD)
	# gestion des Broadcast , à limiter
	elif str(packet.dst) not in table:
		sendpacket(event,of.OFPP_FLOOD)
	else:
	#creation et transmission d'une ligne de table de switch
		dst_port = packet.dst
		msg = of.ofp_flow_mod()
		msg.idle_timeout = 10
		msg.hard_timeout = 30
		msg.actions.append(of.ofp_action_output(port = dst_port))
		event.connection.send(msg)
		log.debug("Installing %s;%i -> %s;%i" %
	(	packet.src, event.ofp.in_port, packet.dst, dst_port))

	gather(packet,event)
	if (int(time.time() -temp))>= 4: 
		temp = time.time()

		with open("stats.txt","a+") as f:
			f.write(str(stats))


		blacklist = detect()

		if len(blacklist) > 0:
			with open("blocked","w+") as f:
				f.write(str(blacklist)+"\n")
			log.debug("removing")
			for src_port in blacklist:
				msg = of.ofp_flow_mod()
				msg.idle_timeout = 100
				msg.hard_timeout = 300
				msg.match.in_port = int(src_port)
				msg.actions.append(of.ofp_action_output(port = 0))
				event.connection.send(msg)
			log.debug("blocking %s",src_port)





def gather(packet,event):
	global stats
	src = str(event.port)
	dst = str(packet.dst)
	log.debug('port %s ----dest adress: %s',src , dst)
	try:
		stats[src+";"+dst] = stats[src+";"+dst] +1
	except:
		stats[src+";"+dst] = 1
	#log.debug("N_comm :%s -- %s",src+";"+dst,stats[src+";"+dst])
def detect():
	global stats
	to_block=[]
	for srcdst,t in stats.iteritems():
		if (t>=400):
			to_block.append(srcdst.split(';')[0])
		with open("blocks.txt","a+") as f:
			f.write(str(srcdst)+"---"+str(t))
			f.write(" "+str(temp))
	stats={}

	return to_block		


	log.debug("temp %s", str(int(time.time())))


	return True



def launch():
	core.openflow.addListenerByName("PacketIn",switch)



