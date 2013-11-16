'''
Created on 25/10/2013

@author: hackturo
'''
#from PruebaPopen import PruebaPopen
from time import sleep
from multiprocessing import Process
import os
import signal
import subprocess
import datetime
import time

class WorkerController(object):
    '''
    classdocs
    '''
    p_monitor = None
    p_miner = None
    
    def __init__(self):
        '''
        Constructor
        '''
        self.p = None
        print "Controller created"
    '''
    def monitor(self):
        i = 0
        while True:        
            print str(i) +" MH/s"
            sleep(1)
            i += 1
        return
    '''        
    
    def monitor(self):
        while True:
            with open("log.txt",'rb') as fh:
                first = next(fh).decode()
                fh.seek(-1024, 2)
                last = fh.readlines()[-1].decode()
            f = open('stats.txt','a')
            if (last.find('avg:') > -1) :
                mhs = last[last.find('avg:')+4 : last.find('u:')-1] + 'MH/s'
                ts = time.time()
                tim = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                f.write(tim+" "+mhs+"\n")
                print tim+" "+mhs
            f.close()
            sleep(5)
    
    def execute_cmd(self, cmd):
        print str(cmd) + " to be executed"
        if str(cmd[0]) == "start":
            self.p_monitor = Process(target = self.monitor)
            self.p_monitor.start()
            # The os.setsid() is passed in the argument preexec_fn so
            # it's run after the fork() and before  exec() to run the shell.
            self.p_miner = subprocess.Popen('bfgminer -o http://api2.bitcoin.cz:8332 -u tomresklin.worker1 -p nDBb37wH --real-quiet > log.txt', shell=True, preexec_fn=os.setsid)
        else:
            if self.p_monitor <> None:
                print "TERMINAT-ing the monitor"
                self.p_monitor.terminate()
            if self.p_miner <> None:
                print "KILL-ing the miner"
                os.killpg(self.p_miner.pid, signal.SIGTERM)
                self.p_miner.kill()
        sleep(1)