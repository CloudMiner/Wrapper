import logging
import asyncore
from EchoServer import EchoServer
from EchoClient import EchoClient
from ServerParser import ServerParser

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )

    address = ('localhost', 0) # let the kernel give us a port
    server = EchoServer(address)
    
    ip, port = server.address # find out what port we were given
    client = EchoClient(ip, port, message=open('instructions.txt', 'r').read())
    
    asyncore.loop()
    '''p = ServerParser()
    p.parse_cmd("")
    p.parse_cmd("ss")
    p.parse_cmd("start")
    p.parse_cmd("stop")
    p.parse_cmd("una prueba")
    p.parse_cmd("start prueba")
    p.parse_cmd("start ltc")
    p.parse_cmd("sTArt lTc")
    p.parse_cmd("sTArt bTc")'''
    
    