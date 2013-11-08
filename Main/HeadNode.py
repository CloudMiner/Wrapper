'''
Created on 20/10/2013

@author: hackturo
'''
import socket
import asyncore
import logging

from time import sleep

class HeadNode(asyncore.dispatcher):
    '''
    Sends messages to the worker node and receives responses.
    '''
    
    def __init__(self, address, message="", chunk_size=512):
        self.busy = False
        self.message = message
        self.to_send = ""
        self.received_data = []
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('HeadNode')
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.logger.debug('connecting to %s', address)
        self.connect(address)
        return
        
    def handle_connect(self):
        self.logger.debug('handle_connect()')
    
    def handle_close(self):
        self.busy = False
        self.logger.debug('handle_close()')
        self.close()
        received_message = ''.join(self.received_data)
        if received_message == self.message:
            self.logger.debug('RECEIVED COPY OF MESSAGE')
        else:
            self.logger.debug('ERROR IN TRANSMISSION')
            self.logger.debug('EXPECTED "%s"', self.message)
            self.logger.debug('RECEIVED "%s"', received_message)
        return
    
    def writable(self):
        self.logger.debug('writable() -> %s', bool(self.to_send))
        return bool(self.to_send)

    def handle_write(self):
        sent = self.send(self.to_send[:self.chunk_size])
        self.logger.debug('handle_write() -> (%d) "%s"', sent, self.to_send[:sent])
        self.to_send = self.to_send[sent:]

    def handle_read(self):
        data = self.recv(self.chunk_size)
        self.logger.debug('handle_read() -> (%d) "%s"', len(data), data)
        self.received_data.append(data)
        self.busy = False
    
    def send_command(self, command):
        self.to_send = command