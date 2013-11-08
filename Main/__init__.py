'''
Created on 20/10/2013

@author: hackturo
'''
import logging
import asyncore

from WorkerNode import WorkerNode
from HeadNode   import HeadNode
from multiprocessing import Process
    
def client_process(addr):
    client = HeadNode(addr)
    client.send_command("start BTC")
    #client.send_command("stop")
    asyncore.loop()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )    

    address = ('localhost', 0) #let the kernel give us a port
    server = WorkerNode(address)
    p1 = Process(target = client_process(server.address))
    p1.start()
    asyncore.loop()
    p1.join()