'''
Created on 25/10/2013

@author: hackturo
'''

from time import sleep
from multiprocessing import Process

class ServerController(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        print "Controller created"
    
    def monitor(self):
        sleep(5)
        i = 0
        while True:        
            print str(i) +" MH/s"
            i += 1
            
    def execute_cmd(self, cmd):
        print str(cmd) + " executed"
        p = Process(target = self.monitor)
        p.start()
        sleep(6)
        p.terminate()
        sleep(1)