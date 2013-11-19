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
import multiprocessing
import array

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
    def monitor_gpu(self):
        f = open('stats.txt','a')
        sleep(10)
        while True:
            with open("log.txt",'rb') as fh:
                first = next(fh).decode()
                fh.seek(-100, 2)
                last = fh.readlines()[-1].decode()
            if (last.find('avg:') > -1) :
                mhs = last[last.find('avg:')+4 : last.find('u:')-1] + 'MH/s'
                ts = time.time()
                tim = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                f.write(tim+" "+mhs+"\n")
                print tim+" "+mhs
            else:
                print last
            sleep(5)
        f.close()
            
    def monitor_cpu(self):
        cpus = multiprocessing.cpu_count()
        last_line = ''
        while True:
            f_stats = open('stats.txt','a')
            sleep(10)
            with open("log.txt",'rb') as f_log:
                first = next(f_log).decode()
                f_log.seek(-100, 2)
                lines = f_log.readlines()
                if(last_line != lines[-1].decode()):
                    last_line = lines[-1].decode()
                    hashes = 0
                    for i in range (1,cpus+1):
                        line_cpu = lines[-i].decode()
                        if (line_cpu.find('hashes') > -1) :
                            hashes = hashes + int(line_cpu[line_cpu.find('hashes')+8:line_cpu.find('hashes')+12])
                            hash_rate = line_cpu[line_cpu.find('hashes')+13:len(line_cpu)-1]
                        else:
                            hashes = 0
                            hash_rate = '???'
                    ts = time.time()
                    tim = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                    f_stats.write(tim+" "+str(hashes)+" "+hash_rate+"\n")
                    print tim+" "+str(hashes)+" "+hash_rate
            f_stats.close()
        
    def execute_cmd(self, cmd):
        print str(cmd) + " to be executed"
        if str(cmd[0]) == "start":
            # The os.setsid() is passed in the argument preexec_fn so
            # it's run after the fork() and before  exec() to run the shell.
            #self.p_miner = subprocess.Popen('bfgminer -o http://api2.bitcoin.cz:8332 -u tomresklin.worker1 -p nDBb37wH --real-quiet 2> log.txt', shell=True, preexec_fn=os.setsid)
            self.p_miner = subprocess.Popen('/usr/bin/minerd -a sha256d -o stratum+tcp://stratum.bitcoin.cz:3333 -O cloudminer.worker1:9868UyAN 2>log.txt', shell=True, preexec_fn=os.setsid)
            self.p_monitor = Process(target = self.monitor_cpu)
            #sleep(5)
            self.p_monitor.start()
        else:
            if self.p_monitor <> None:
                print "TERMINAT-ing the monitor"
                self.p_monitor.terminate()
            if self.p_miner <> None:
                print "KILL-ing the miner"
                os.killpg(self.p_miner.pid, signal.SIGTERM)
                self.p_miner.kill()
        sleep(1)