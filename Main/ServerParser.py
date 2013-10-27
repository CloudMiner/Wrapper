'''
Created on 25/10/2013

@author: hackturo
'''

class ServerParser(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        print "Parser created"
        
    def parse_cmd(self, cmd):
        l1 = cmd.split() #Aqui se puede anyadir el parametro correspondiente al separador (si es el espacio no se pone)
        #for s in l1:
        #    print s
        if len(l1) < 1:
            print "ERR: no commands issued..."
        elif len(l1) == 1:
            if l1[0].lower() == "stop":
                print "stop mining!"
            elif l1[0].lower() == "start":
                print "ERR, crypto-currency parameter missing..."
            else:
                print "ERR, command not recognized: " + l1[0]
        elif len(l1) == 2:
            if l1[0].lower() == "start":
                if l1[1].lower() == "btc":
                    print "start mining for BitCoins!"
                elif l1[1].lower() == "ltc":
                    print "start mining for LiteCoins!"
                else:
                    print "ERR, crypto-currency not recognized: " + l1[1]
            else:
                print "ERR, command not recognized: " + l1[0]
        return l1