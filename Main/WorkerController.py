'''
Created on 25/10/2013

@author: hackturo
'''
#from PruebaPopen import PruebaPopen
#from time import sleep
#from multiprocessing import Process
        
from time import sleep
from multiprocessing import Process

class WorkerController(object):
    '''
    classdocs
    '''
    p = None
    
    def __init__(self):
        '''
        Constructor
        '''
        self.p = None
        print "Controller created"
    
    def monitor(self):
        i = 0
        while True:        
            print str(i) +" MH/s"
            sleep(1)
            i += 1
        return
            
    '''
    def monitor():
    while True:
        with open("C:\\miners\\cgminer\\logfile.txt",'rb') as fh:
            first = next(fh).decode()
            fh.seek(-1024, 2)
            last = fh.readlines()[-1].decode()
        f = open('result.txt','a')
        f.write(last[last.find(')')+2:last.find('M')] + "MH/s\n")
        f.close()
        sleep(5)
    '''
           
    def execute_cmd(self, cmd):
        print str(cmd) + " executed"
        if str(cmd[0]) == "start":
            self.p = Process(target = self.monitor)
            self.p.start()
        elif self.p <> None:
            self.p.terminate()
        sleep(1)