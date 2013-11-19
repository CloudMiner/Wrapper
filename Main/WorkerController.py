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
    
    def tail(self,f, n, offset=None):
        """Reads a n lines from f with an offset of offset lines.  The return
        value is a tuple in the form ``(lines, has_more)`` where `has_more` is
        an indicator that is `True` if there are more lines in the file.
        """
        avg_line_length = 60
        to_read = n + (offset or 0)
    
        while 1:
            try:
                f.seek(-(avg_line_length * to_read), 2)
            except IOError:
                # woops.  apparently file is smaller than what we want
                # to step back, go to the beginning instead
                f.seek(0)
            pos = f.tell()
            lines = f.read().splitlines()
            if len(lines) >= to_read or pos == 0:
                return lines[-to_read:offset and -offset or None], \
                       len(lines) > to_read or pos > 0
            avg_line_length *= 1.3
    
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
            sleep(20)
            with open("log.txt",'rb') as f_log:
                lines = self.tail(f_log,cpus)
                #print lines
                #print lines[0][0]+"\n"
                #print lines[0][len(lines)-1]+"\n"
                '''first = next(f_log).decode()
                f_log.seek(-100, 2)
                lines = f_log.readlines()
                '''
                if(last_line != lines[0][-1]):#.decode()):
                    last_line = lines[0][-1]#.decode()
                    hashes = 0
                    #for i in range (1,cpus+1):
                    for line_cpu in lines[0]:
                        #line_cpu = lines[0][i]#.decode()
                        if (line_cpu.find('hashes') > -1) :
                            hashes = hashes + int(line_cpu[line_cpu.find('hashes')+8:line_cpu.find('hashes')+12])
                            hash_rate = line_cpu[line_cpu.find('hashes')+13:len(line_cpu)]
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