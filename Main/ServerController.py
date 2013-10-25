'''
Created on 25/10/2013

@author: hackturo
'''

class ServerController(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        print "Controller created"
    
    def execute_cmd(self, cmd):
        print cmd + " executed"