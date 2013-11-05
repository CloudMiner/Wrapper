'''
Created on 20/10/2013

@author: hackturo
'''
import logging
import asyncore

from WorkerNode import WorkerNode
from HeadNode   import HeadNode

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )

    address = ('localhost', 0) # let the kernel give us a port
    server = WorkerNode(address)
    
    ip, port = server.address # find out what port we were given
    client = HeadNode(ip, port, message=open('instructions.txt', 'r').read())
    
    asyncore.loop()
