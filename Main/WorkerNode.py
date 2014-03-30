#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 20/10/2013

@author: hackturo
'''

from time import sleep
import WorkerController
import WorkerParser
import asyncore
import atexit
import logging
import multiprocessing
import pymysql
import socket
import sys
import time
import os
import platform
        
    
class WorkerNode(asyncore.dispatcher):

    '''
    Receives connections and establishes handlers for each client.
    '''

    def __init__(self, address):
        self.logger = logging.getLogger('WorkerNode')
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_error = True
        while socket_error:
            try:
                self.bind(address)
                socket_error = False        
            except socket.error, msg:
                print 'encountered following error while configuring connection:'
                print '[ERROR] ' + msg[1]
                print 'trying again in 20 seconds...'
                sleep(20)
        #self.bind(address)
        self.id_worker = self.generate_id()
        self.address = self.socket.getsockname()
#         print "IP: " , self.address[0]
#         print "port: " , self.address[1]
#         print "" 
        self.machine_name = socket.gethostname()
        #print "ADDRESS: "
        #print self.address
        self.is64bits  = sys.maxsize > 2 ** 32
        self.num_cpus = multiprocessing.cpu_count()
        self.platform = platform.system()
        if(self.platform.find('Windows')):
            self.plat_type = platform.linux_distribution()[0]
            self.plat_version = platform.linux_distribution()[1]
        elif(self.platform.find('Linux')):
            self.plat_type = "unique"
            self.plat_version = platform.win32_ver()[0] 
        else:
            pass

        if(self.is64bits):
            self.plat_arch = '64bit'
        else:
            self.plat_arch = '32bit' 
        
        print os.path.dirname(__file__)
        
        self.conn_mysql = pymysql.connect(host='127.0.0.1', port=3306, user='clminer', passwd='cloudminer2014', db='cloudminer')
        self.cur = self.conn_mysql.cursor()
        
        self.ddbb_obtain_platform_id()
        self.ddbb_obtain_machine_id()
        
        #cur.execute("INSERT INTO machine (name, ip, port, platform_id) VALUES ()")
        
        self.parser = WorkerParser.WorkerParser()
        self.controller = \
            WorkerController.WorkerController(invoker=self)
        self.logger.debug('binding to %s', self.address)
        self.listen(1)
        return 
    
    def ddbb_obtain_machine_id(self):
        self.cur.execute("SELECT * FROM machine")
        struct = self.cur.description
        i = 0;
        id_idx = -1
        name_idx = -1
        ip_idx = -1
        port_idx = -1
        plat_id_idx = -1
        for s in struct:
#             print(s)
            if(s[0]=='id'):
                id_idx = i
            elif(s[0]=='name'):
                name_idx = i
            elif(s[0]=='ip'):
                ip_idx = i
            elif(s[0]=='port'):
                port_idx = i
            elif(s[0]=='platform_id'):
                plat_id_idx = i
            i += 1 
        if(id_idx != -1 and name_idx != -1 and ip_idx != -1 and port_idx != -1 and plat_id_idx != -1):
#             print id_idx , " -- " , name_idx , " -- " , ip_idx , " -- " , port_idx , " -- " , plat_id_idx
#             print ""
            pass
        else:
            print("Unable to obtain data from cloudminer.platform, terminating now...")
            #throw error and quit!!
            
        self.machine_DDBB_id = -1    
        for row in self.cur:
#             print row[id_idx] , " -- " , row[name_idx] , " -- " , row[ip_idx] , " -- " , row[port_idx] , " -- " , row[plat_id_idx]
#             print ""
            
            if(row[name_idx]==self.machine_name and row[ip_idx]==self.address[0] and row[port_idx]==self.address[1] and row[plat_id_idx]==self.platform_DDBB_id):
                self.machine_DDBB_id = row[id_idx]
                
        #self.conn.commit()
        if(self.machine_DDBB_id == -1):
            query = "INSERT INTO machine (name, ip, port, alive, platform_id) VALUES (" \
                             + "'" + self.machine_name + "', " \
                             + "'" + self.address[0] + "'," \
                             + str(self.address[1]) + "," \
                             + "'T'," \
                             + str(self.platform_DDBB_id) + ");"
#             print query
#             print ""
            self.cur.execute(query)
            self.conn_mysql.commit()
            
            query = "SELECT id FROM machine WHERE " \
                             + "name = '" + self.machine_name + "' " \
                             + " AND ip = '" + self.address[0] + "'" \
                             + " AND port = " + str(self.address[1]) \
                             + " AND platform_id = " + str(self.platform_DDBB_id) + ";"
#             print query
#             print ""
            self.cur.execute(query)
            for row in self.cur:
                if(self.machine_DDBB_id == -1):
                    self.machine_DDBB_id = row[0]
        else:
            query = "UPDATE machine SET alive = 'T' WHERE id = " + str(self.machine_DDBB_id) + ";"
            self.cur.execute(query)
            self.conn_mysql.commit()
            
        print "machine_DDBB_id: " , self.machine_DDBB_id
        print ""
    
    def ddbb_obtain_platform_id(self):
        self.cur.execute("SELECT * FROM platform")
        struct = self.cur.description
        i = 0;
        id_idx = -1
        os_idx = -1
        type_idx = -1
        arch_idx = -1
        version_idx = -1
        for s in struct:
#             print(s)
            if(s[0]=='id'):
                id_idx = i
            elif(s[0]=='os'):
                os_idx = i
            elif(s[0]=='type'):
                type_idx = i
            elif(s[0]=='arch'):
                arch_idx = i
            elif(s[0]=='version'):
                version_idx = i
            i += 1 
        if(id_idx != -1 and os_idx != -1 and type_idx != -1 and arch_idx != -1 and version_idx != -1):
#             print id_idx , " -- " , os_idx , " -- " , type_idx , " -- " , arch_idx , " -- " , version_idx
            pass
        else:
            print("Unable to obtain data from cloudminer.platform, terminating now...")
            #throw error and quit!!
            
        self.platform_DDBB_id = -1    
        for row in self.cur:
#             print row[id_idx] , " -- " , row[os_idx] , " -- " , row[type_idx] , " -- " , row[arch_idx] , " -- " , row[version_idx]
            
            if(row[os_idx]==self.platform and row[type_idx]==self.plat_type and row[arch_idx]==self.plat_arch and row[version_idx]==self.plat_version):
                self.platform_DDBB_id = row[id_idx]
        
        #self.conn.commit()
        if(self.platform_DDBB_id == -1):
            #self.cur = self.conn_mysql.cursor()
            self.cur.execute("INSERT INTO platform (os, type, arch, version) VALUES (" \
                             + "'" + self.platform + "', " \
                             + "'" + self.plat_type + "'," \
                             + "'" + self.plat_arch + "'," \
                             + "'" + self.plat_version + "');")
            self.conn_mysql.commit()
            self.cur.execute("SELECT id FROM platform WHERE " \
                             + "os = '" + self.platform + "' " \
                             + " AND type = '" + self.plat_type + "'" \
                             + " AND arch = '" + self.plat_arch + "'" \
                             + " AND version = '" + self.plat_version + "';")
            for row in self.cur:
                if(self.platform_DDBB_id == -1):
                    self.platform_DDBB_id = row[0]
        
        print "platform_DDBB_id: " , self.platform_DDBB_id
    
    
    def ddbb_delete_machine(self):
        if(self.machine_DDBB_id!=None):
            query = "DELETE FROM machine WHERE id = " + str(self.machine_DDBB_id) + ";"
    #         print query
            self.cur.execute(query)
            self.conn_mysql.commit()
        else:
            print " <ERROR> unable to delete machine (machine_id not set)"
    
    
    def ddbb_machine_end(self):
        if(self.machine_DDBB_id!=None):
            query = "UPDATE machine SET alive = 'F' WHERE id = " + str(self.machine_DDBB_id) + ";"
            self.cur.execute(query)
            self.conn_mysql.commit()
        else:
            print " <ERROR> unable to delete machine (machine_id not set)"
    
    def get_worker_id(self):
        return self.id_worker
    
    def generate_id(self):
        ts = str(int(time.time()))
        ts1 = ts[0]+ts[len(ts)-1]
        return "Worker"+ts
        
    def handle_accept(self):

        # Called when a client connects to our socket

        client_info = self.accept()

        # self.logger.debug('handle_accept() -> %s', client_info[1])
        # Create Handler

        WorkerHandler(sock=client_info[0], srv_parser=self.parser,
                      srv_ctrl=self.controller, chunk_size=256)

        # We only want to deal with one client at a time,
        # so close as soon as we set up the handler.
        # Normally you would not do this and the server
        # would run forever or until it received instructions
        # to stop.

        # self.handle_close()
        # return

    def handle_close(self):

        # self.logger.debug('pseudo handle_close()')

        self.close()
        return


    def quit(self):
        #self.ddbb_delete_machine()
        self.ddbb_machine_end()
        self.cur.close()
        self.controller.quit()
        self.conn_mysql.close()
        

class WorkerHandler(asyncore.dispatcher):
    """Handles command messages from a single client."""

    def __init__(
        self,
        sock,
        srv_parser,
        srv_ctrl,
        chunk_size=256,
        ):

        self.chunk_size = chunk_size
        self.parser = srv_parser
        self.controller = srv_ctrl

        # self.logger     = logging.getLogger('WorkerHandler%s' % str(sock.getsockname()))

        asyncore.dispatcher.__init__(self, sock=sock)
        self.data_received = ''
        self.data_to_write = []
        return

    def work(self):
        data = self.data_received
        print "We have received the following command: " + data
        self.controller.execute_cmd(data.split())
        #if len(data) > 0:
        #    cmd = self.parser.parse_cmd(data)
        #    self.controller.execute_cmd(cmd)

    def writable(self):
        """We want to write if we have received data."""

        response = bool(self.data_to_write)

        # self.logger.debug('writable() -> %s', response)

        return response

    def handle_write(self):
        """Write as much as possible of the most recent message we have received."""

        data = self.data_to_write.pop()
        sent = self.send(data[:self.chunk_size])
        if sent < len(data):
            remaining = data[sent:]
            self.data.to_write.append(remaining)

        # self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent])

        if not self.writable():
            self.handle_close()

    def handle_read(self):
        """Read an incoming message from the client and put it into our outgoing queue."""

        self.data_received = self.recv(self.chunk_size)

        # self.logger.debug('handle_read() -> (%d) "%s"', len(self.data_received), self.data_received)

        self.data_to_write.insert(0, self.data_received)  # Callback

    def handle_close(self):

        # self.logger.debug('workerhandler closed')

        self.close()
        self.work()  # work after close this socket

def exit_handler(worker):
    print 'ending application :: ' +worker.get_worker_id()+ '!!'
    worker.quit()
    #worker.controller.quit()
        
if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s')

    address_server = ('0.0.0.0', 0)
    w = WorkerNode(address_server)
    atexit.register(exit_handler, w)
    asyncore.loop()
