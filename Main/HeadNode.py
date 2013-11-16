'''
Created on 14/11/2013

@author: hackturo
'''
import logging
import asyncore
import subprocess
from time import sleep
import datetime
#import time

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
    sleep(30)
    task_process(address_client, "stop")
    
    '''ts = time.time()
    time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print time'''