'''
Created on 14/11/2013

@author: hackturo
'''
import logging
import asyncore
import subprocess
from time import sleep
import datetime
import time

from time import sleep
from TaskMaster import TaskMaster

def task_process(addr, task):
    print "inicializa el TaskMaster"
    connector = TaskMaster(addr)
    print "TaskMaster manda el comando: "+str(task)    
    connector.send_command(task)
    asyncore.loop()
    print "CALLBACK:"+connector.get_callback()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s',
                        )    

    address_client = ('127.0.0.1', 5006)
    task_process(address_client, "start BTC")
    print "==============COMANDO 1 TERMINADO==================="
    sleep(60)
    task_process(address_client, "stop")
    print "==============COMANDO 2 TERMINADO===================" 
    
    '''
    ts = time.time()
    time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print time
    
    with open("log.txt",'r') as fh:
        first = next(fh).decode()
        l = len(first)
        fh.seek(-100, 2)
        last = fh.readlines()[-1].decode()
        f = open('stats.txt','a')
        if (last.find('avg:') > -1) :
            mhs = last[last.find('avg:')+4 : last.find('u:')-1] + 'MH/s'
            ts = time.time()
            tim = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            f.write(tim+" "+mhs+"\n")
            print tim+" "+mhs
        else:
            f.write(last)
            print last
    '''