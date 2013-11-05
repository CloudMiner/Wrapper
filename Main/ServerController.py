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
        i = 0
        while True:        
            print str(i) +" MH/s"
            i += 1
            sleep(5) # este sleep si debería hacer paramétrico, indica el tiempo de refresco, debería ser el mismo que para el miner
            
    def execute_cmd(self, cmd):
        print str(cmd) + " executed"
        p = Process(target = self.monitor)
        p.start()
        sleep(30) # este sleep es innecesario, se reemplazaría por la recepción de la orden "STOP"
        p.terminate()
        sleep(1)