'''
Created on 25/10/2013

@author: hackturo
'''
import re
import sys
import time
import datetime
import pymongo
import subprocess
import threading 
# import datetime
# import multiprocessing

class WorkerController(object):
    '''
    classdocs
    '''
    
    def __init__(self):
        '''
        Constructor
        '''
        self.p_miner = None
        self.t_monitor = None
        self.is64bits = (sys.maxsize > 2**32)
        self.platform = sys.platform
        print "Platform: " + self.platform
        print "Is 64 bits: " + str(self.is64bits)
        print "Controller created"
     
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
    '''
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
    '''
    '''        
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
#                 first = next(f_log).decode()
#                 f_log.seek(-100, 2)
#                 lines = f_log.readlines()
                
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
    ''' 
    def insert_data(self ,id_worker ,id_miner ,currency ,hash_rate ,datetime ):
        db_connection = pymongo.Connection("localhost", 27017)
        cloudminerDB = db_connection.cloudminerDB
        col_status = cloudminerDB['col_status']
        status = {
                  "id_worker" : id_worker,
                  "id_miner"  : id_miner,
                  "currency"  : currency,
                  "hash_rate" : hash_rate,
                  "datetime"  : datetime
                 }
        col_status.insert(status)
        print "Item inserted!!!"
        
    def monitor(self):  
        while self.p_miner.poll() == None:
            line = self.p_miner.stdout.readline()
            if line: 
                print line
#                 id_worker = 1
#                 id_miner = 1
#                 currency = "BTC"
#                 hash_rate = 5.1549
#                 datetime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
#                 self.insert_data(id_worker ,id_miner ,currency ,hash_rate ,datetime)
            #monitoring time      
            #time.sleep(3)
        print "monitor finished"
    
    def start_miner(self, id_miner):
        #we need to use id_miner to obtain miner_cmd from its shell script
        miner_cmd = [
                     "/home/hackturo/Software/miners/cpuminer-2.3.2/minerd",
                     "-a","sha256d",
                     "-o","stratum+tcp://stratum.bitcoin.cz:3333",
                     "-O","cloudminer.worker1:9868UyAN"
                    ]
        self.p_miner = subprocess.Popen(miner_cmd,shell=False, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        self.t_monitor = threading.Thread(target=self.monitor)  
        self.t_monitor.start()  
    
    def stop_miner(self):
        if self.p_miner <> None:
            print "Terminating the miner"
            if self.p_miner.poll() == None:
                self.p_miner.terminate()
            self.t_monitor.join(timeout=10)
            self.p_miner = None
            self.t_monitor = None
            print "Miner terminated"
                
    def execute_cmd(self, cmd):
        print str(cmd) + " to be executed"
        opcode = str(cmd[0])        
        
        if opcode == "start":
            self.stop_miner()
            id_miner = str(cmd[1])
            self.start_miner(id_miner)
            # The os.setsid() is passed in the argument preexec_fn so
            # it's run after the fork() and before  exec() to run the shell.
            #self.p_miner = subprocess.Popen('bfgminer -o http://api2.bitcoin.cz:8332 -u tomresklin.worker1 -p nDBb37wH --real-quiet 2> log.txt', shell=True, preexec_fn=os.setsid)
            #self.p_miner = subprocess.Popen('/usr/bin/minerd -a sha256d -o stratum+tcp://stratum.bitcoin.cz:3333 -O cloudminer.worker1:9868UyAN 2>log.txt', shell=True, preexec_fn=os.setsid)
            #self.p_monitor = Process(target = self.monitor_cpu)
            #sleep(5)
            #self.p_monitor.start()
        elif opcode == "stop":
            self.stop_miner()
#             if self.p_monitor <> None:
#                 print "TERMINAT-ing the monitor"
#                 self.p_monitor.terminate()
            
                #os.killpg(self.p_miner.pid, signal.SIGTERM)
                #self.p_miner.kill()
        else :
            print "Unknown Command"