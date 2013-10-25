import logging
import asyncore
from EchoServer import EchoServer
from EchoClient import EchoClient

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )

    address = ('localhost', 0) # let the kernel give us a port
    server = EchoServer(address)
    
    ip, port = server.address # find out what port we were given
    client = EchoClient(ip, port, message=open('instructions.txt', 'r').read())
    
    asyncore.loop()
    
    