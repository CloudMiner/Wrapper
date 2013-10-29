#import subprocess
from subprocess import call

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
        #call("O:\\Tom\\miners\\bfgminer3.4\\bfgminer -o http://api2.bitcoin.cz:8332 -u tomresklin.worker1 -p nDBb37wH",shell=True)
        p = call("O:\\Tom\\miners\\bfgminer3.4\\bfgminer -h", shell=True)
        #p = subprocess.Popen('O:\\Tom\\miners\\bfgminer3.4\\bfgminer -o http://api2.bitcoin.cz:8332 -u tomresklin.worker1 -p nDBb37wH', shell=True)
        #p = subprocess.Popen('O:\\Tom\\miners\\bfgminer3.4\\bfgminer', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #p = subprocess.Popen('dir', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        '''for line in p.stdout.readlines():
            print line,
        retval = p.wait()'''
    
    