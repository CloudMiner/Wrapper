import subprocess
from subprocess import call
from threading import Thread

class PruebaPopen(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
       
    def prueba_algo(self):
        #call("dir",shell=True)
        #call('C:\\Users\\Tomas\\miners\\cgminer\\cgminer -o stratum.btcguild.com:3333 -u nilksermot_1 -p 123 2>logfile2.txt',Shell=True)
        #call("O:\\Tom\\miners\\bfgminer3.4\\bfgminer -o http://api2.bitcoin.cz:8332 -u tomresklin.worker1 -p nDBb37wH",shell=True)
        #p = call("O:\\Tom\\miners\\bfgminer3.4\\bfgminer -h", shell=True)
        #p = subprocess.Popen('C:\\Users\\Tomas\\miners\\cgminer\\cgminer -o mint.bitminter.com:8332 -u nilksermot_worker1 -p 123', shell=True)
        #p = subprocess.Popen('C:\\Users\\Tomas\\miners\\cgminer\\cgminer -o stratum.btcguild.com:3333 -u nilksermot_1 -p 123 2>logfile2.txt', shell=True)
        p = subprocess.Popen('C:\\miners\\cgminer\\cgminer.exe -o eu-stratum.btcguild.com:3333 -u nilksermot_1 -p 1', shell=True)
        #p = subprocess.Popen('O:\\Tom\\miners\\cgminer\\cgminer -h',shell=True)
        #p = subprocess.Popen('O:\\Tom\\miners\\bfgminer3.4\\bfgminer', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #p = subprocess.Popen('dir', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)    
    