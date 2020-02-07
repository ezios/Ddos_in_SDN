import libvirt as lv
import sys
import time
import subprocess as p
import argparse
def usage():	
	print('usage : vmtool --function [optional] <arguments>')
	print("--startall : Start all virtual machines and network,the connect by ssh\
		         \n--stopall : Stop all running virtual network and machines\
		         \n--stop or --start <domain_names> [one or more separated by space] , kill or run domain")




try:
	arg = sys.argv[1]
except:
	usage()



#return ip adresses of active vm in the bridge <net>
def fetch_adress(net):
	connec =  -1
	adresses = []
	while connec ==-1:
		arp = str(p.check_output("arp -e", shell=True))
		connec = arp.rfind(net)
	res = str(arp).split("\\n")
	for line in res:
		if line.rfind(net) > -1:
			adresses.append(line[0:16].rstrip())
	return(adresses)


def netstart(netname):
	network = conn.networkLookupByName(netname)
	if network.isActive():
		print("/!\\",netname,"already active")
		return 0
	network.create()
	if network.isActive():
		print("[+] ",netname," is on")
		return network.bridgeName()
	else:
		print("network")
def netstop(netname):
	try:
		network = conn.networkLookupByName(netname)
	except:
		print("no virtual network named ",netname)
		return 
	if network.isActive():
		network.destroy()
		print("[-] ",netname,"destroyed")
	else:
		print(" Network already off")

def vmstart(vmname):
	try:
		vm = conn.lookupByName(vmname)
	except:
		return
	if vm.isActive():
		print('/!\\',vmname,'is already running')
		return 0
	else:
		vm.create()
	if vm.isActive():
		print("[+] ",vmname,' started')
		
def vmstop(vmname):
	try:
		vm = conn.lookupByName(vmname)
	except:
		return
	if vm.isActive():
		vm.destroy()
		print("[-] ",vmname,"turned off")
	else:
		print("/!\\ ",vmname," is already off")
	
		
def startall():
	global conn
	bridge = netstart('vnet2')
	domainNames = conn.listDefinedDomains()
	if len(domainNames) == 0:
		print('All Vm already are in running status')
	for vm in domainNames:
		n = vmstart(vm)
	
	n_vm = len(domainNames)

	adresses = []
	while len(adresses) != n_vm:
		adresses = fetch_adress(bridge)
	for rhost in adresses:
		print("connecting to ",rhost)
		p.Popen("gnome-terminal -- ssh root@"+rhost,stdout=p.PIPE,stderr=None,shell=True)

#+" \'./run\'"

	

def stopall():
	netstop('vnet2')
	vmstop('debian2')
	vmstop('debian1')



def listactive():
	global conn
	domainNames=[]
	domainIDs = conn.listDomainsID()
	if domainIDs == None:
		print('Failed to get a list of domain IDs',file = sys.stderr)
	if len(domainIDs) != 0:
		for domainID in domainIDs:
			domain = conn.lookupByID(domainID)
			domainNames.append(domain.name())
	if len(domainNames) == 0:
		print("No active domain")
	else:
		for vm_name in domainNames:
			print(" ",vm_name)	


conn = lv.open('qemu:///system')
if conn == None :
		print("failed to connect to qemu")
		sys.exit()
if len (sys.argv)==2:
	if arg == "--startall":
		startall()
		print("\n")
	elif arg == "--stopall":
		stopall()
	elif arg == "--listactive":
		listactive()
	else:
		usage()
if len(sys.argv)>=3:
	try:
		arg = sys.argv[2:]
	except:
		print("error")
		sys.exit()
	if sys.argv[1]=="--stop":
		for vm in arg:
			vmstop(vm)
	elif sys.argv[1]=="--start":
		for vm in arg:
			vmstart(vm)
	else:
		usage()
