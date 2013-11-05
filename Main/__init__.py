import logging
import asyncore
from EchoServer import EchoServer
from EchoClient import EchoClient
from ServerParser import ServerParser
#from PruebaPopen import PruebaPopen

#from time import sleep
#from multiprocessing import Process

'''def monitor():
    while True:
        with open("C:\\miners\\cgminer\\logfile.txt",'rb') as fh:
            first = next(fh).decode()
            fh.seek(-1024, 2)
            last = fh.readlines()[-1].decode()
        f = open('result.txt','a')
        f.write(last[last.find(')')+2:last.find('M')] + "MH/s\n")
        f.close()
        sleep(5)'''

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )

    address = ('localhost', 0) # let the kernel give us a port
    server = EchoServer(address)
    
    ip, port = server.address # find out what port we were given
    client = EchoClient(ip, port, message=open('instructions.txt', 'r').read())
    
    asyncore.loop()
    '''
    
    p = Process(target = monitor)
    p.start()
    sleep(30)
    p.terminate()'''