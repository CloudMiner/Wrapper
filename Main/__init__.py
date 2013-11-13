'''
Created on 20/10/2013

@author: hackturo
'''
import logging
import asyncore

from WorkerNode import WorkerNode
from TaskMaster   import TaskMaster
from multiprocessing import Process
    
def client_process(addr):
    client = TaskMaster(addr)    
    client.send_command("start BTC")
    asyncore.loop()
    print "CALLBACK:"+client.get_callback()
    
def server_process(addr):
    WorkerNode(addr) 
    #asyncore.loop() 
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )    

    address_server = ('0.0.0.0', 5007)
    address_client = ('127.0.0.1', 5007)
#     server = WorkerNode(address)    
    p1 = Process(target = server_process(address_server))
    p2 = Process(target = client_process(address_client))
    p1.start()    
    p2.start()  
    p2.join()
    print "==============COMANDO 1 TERMINADO==================="    
    p1.join()