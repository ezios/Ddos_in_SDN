import requests
import sys
import time
#vider le fichier
with open("acces_log","w") as f:
	f.write("")
#prend coomme argument le port et l'adresse du server	
adresse_port = sys.argv[1]

print(adresse_port)
print("running")

url = "http://"+adresse_port
while True:
	a=time.time()
	r= requests.get(url)
	a =str(time.time()-a)
	with open("acces_log","a+") as f:
		f.write(a+"\n")
	time.sleep(1)

