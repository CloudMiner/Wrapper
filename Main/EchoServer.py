'''
Created on 20/10/2013

@author: hackturo
'''
import socket
import asyncore
import logging
from ServerParser import ServerParser
from ServerController import ServerController
# import ServerLauncher

class EchoServer(asyncore.dispatcher):
    """Receives connections and establishes handlers for each client.
    """
        
    parser     = ServerParser()        #gets parser instance
    controller = ServerController()    #gets controller instance 
        
    def __init__(self, address):
        self.logger = logging.getLogger('EchoServer')
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug('binding to %s', self.address)
        self.listen(1)
        return

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        self.logger.debug('handle_accept() -> %s', client_info[1])
        # Create Handler
        EchoHandler(sock = client_info[0], \
                    srv_parser = self.parser,\
                    srv_ctrl = self.controller,\
                    chunk_size=256)
        # We only want to deal with one client at a time,
        # so close as soon as we set up the handler.
        # Normally you would not do this and the server
        # would run forever or until it received instructions
        # to stop.
        
        self.handle_close()
        return
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
        return

class EchoHandler(asyncore.dispatcher):
    """Handles echoing messages from a single client.
    """
    
    def __init__(self, sock, srv_parser, srv_ctrl, chunk_size=256):
        self.chunk_size = chunk_size
        self.parser     = srv_parser
        self.controller = srv_ctrl
        self.logger     = logging.getLogger('EchoHandler%s' % str(sock.getsockname()))
        asyncore.dispatcher.__init__(self, sock=sock)
        self.data_to_write = []
        return
    
    def writable(self):
        """We want to write if we have received data."""
        response = bool(self.data_to_write)
        self.logger.debug('writable() -> %s', response)
        return response
    
    def handle_write(self):
        """Write as much as possible of the most recent message we have received."""
        data = self.data_to_write.pop()
        sent = self.send(data[:self.chunk_size])
        if sent < len(data):
            remaining = data[sent:]
            self.data.to_write.append(remaining)
        self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent])
        if not self.writable():
            self.handle_close()

    def handle_read(self):
        """Read an incoming message from the client and put it into our outgoing queue."""
        data = self.recv(self.chunk_size)
        self.logger.debug('handle_read() -> (%d) "%s"', len(data), data)
        cmd = self.parser.parse_cmd(data)
        self.controller.execute_cmd(cmd)
        #sself.launcher.execute_cmd(data)
        
        self.data_to_write.insert(0, data)
    
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()