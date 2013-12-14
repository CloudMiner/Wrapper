#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 25/10/2013

@author: hackturo
'''

import re
import sys
import time
import datetime
from time import sleep

import pymongo
import subprocess
import threading


class WorkerController(object):

    '''
    classdocs
    '''

    def __init__(self, invoker):
        '''
        Constructor
        '''
        self.invoker   = invoker
        self.address   = invoker.address
        self.id_worker = invoker.id_worker
        self.is64bits  = sys.maxsize > 2 ** 32
        plat = sys.platform
        if(plat.find('windows')):
            self.platform  = 'windows'
        elif(plat.find('linux')):
            self.platform  = 'linux'
        else:
            self.platform  = plat
        #self.platform  = sys.platform
        
        self.actual_miner_vars = {} # empty two-level dictionary
        
        #self.id_miner  = None
        #self.currency_cpu  = None
        #self.currency_gpu  = None
        #self.p_miner_cpu   = None     # Miner Process on CPU
        #self.p_miner_gpu   = None     # Miner Process on GPU
        #self.t_monitor_cpu = None   # Monitor Thread
        #self.t_monitor_gpu = None   # Monitor Thread
        #self.miner_cpu_ok = None
        #self.miner_gpu_ok = None
        self.miner_cmds = {}
        self.miner_cmds['m_cpu'] = [
                '../Miners/minerd',
                '-a',
                'sha256d',
                '--benchmark'
                ]
        self.miner_cmds['m_gpu'] = [
                'bfgminer',
                '--benchmark',
                '--real-quiet'
                ]

        print 'Worker: ' + self.id_worker
        print 'Platform: ' + self.platform
        print 'Is 64 bits: ' + str(self.is64bits)
        print 'Controller created'
        self.ddbb_insert_worker()

    def parse_hashes(self, line):
        s = line.split()
        mh = None
        if re.search(r'hash/s', line) and len(s) == 8:
            hashes = float(s[6])
            metric = s[7]
            if metric == 'khash/s':
                hashes /= 1024
            mh = hashes
            print 'MH--->' + str(mh)
        return mh


    def ddbb_insert_worker(self):
        db_connection = pymongo.Connection('localhost', 27017)
        cloudminerDB = db_connection.cloudminerDB
        #col_status = cloudminerDB['col_status']
        col_active_workers = cloudminerDB['col_active_workers']
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        if(self.is64bits):
            architecture = '64 bits'
        else:
            architecture = '32 bits'
        worker = {
            'id_worker'   : self.id_worker,
            'platform'    : self.platform,
            'architecture': architecture,
            'start_time'  : timestamp,
            'start_time2' : ts,
            #'IP'         : '127.0.0.1'
            'IP'          : self.address[0],
            'port'        : self.address[1],
            }

        col_active_workers.insert(worker)
        print 'Item inserted!!!'


    def ddbb_remove_worker(self):
        db_connection = pymongo.Connection('localhost', 27017)
        cloudminerDB = db_connection.cloudminerDB
        #col_status = cloudminerDB['col_status']
        col_active_workers = cloudminerDB['col_active_workers']
        worker = {
            'id_worker': self.id_worker,
            }

        col_active_workers.remove(worker)


    def ddbb_insert_worker_stats(self, hash_rate, miner_id):
    #def insert_data(self, hash_rate, miner_id):
        #currency = self.actual_miner_vars[miner_id]['currency']
        db_connection = pymongo.Connection('localhost', 27017)
        cloudminerDB = db_connection.cloudminerDB
        #col_status = cloudminerDB['col_status']
        col_worker_stats = cloudminerDB['col_worker_stats']
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        status = {
            'id_worker': self.id_worker,
            'id_miner': miner_id,
            #'currency': currency,
            'hash_rate': hash_rate,
            'datetime' : timestamp,
            'datetime2' : ts,
            }

        col_worker_stats.insert(status)
        print 'Item inserted!!!'

    def monitor_minerd(self):
        num_lines = 0
        hash_rate = 0  # MH/s
        while self.actual_miner_vars['m_cpu']['p_miner'].poll() == None:
            line = self.actual_miner_vars['m_cpu']['p_miner'].stdout.readline()
            if line:
                line_hashes = self.parse_hashes(line)
                
                if line_hashes:
                    self.actual_miner_vars['m_cpu']['works_ok'] = True
                    hash_rate += line_hashes
                    num_lines += 1
                    num_lines %= 4
                    if num_lines == 0:
                        #self.insert_data(hash_rate,'m_cpu')
                        self.ddbb_insert_worker_stats(hash_rate,'m_cpu')
                        print str(hash_rate)
                        hash_rate = 0  # reset hash count
                else:
                    if self.actual_miner_vars['m_cpu']['works_ok'] == None and re.search(r'Try', line):
                        self.actual_miner_vars['m_cpu']['works_ok'] = False
                    print line

            # monitoring time
            # time.sleep(3)

        print 'monitor_minerd finished'

    def monitor_bfgminer(self):
        while self.actual_miner_vars['m_gpu']['p_miner'].poll() == None:
            line = self.actual_miner_vars['m_gpu']['p_miner'].stdout.readline()
            if line:
                hash_rate = self.parse_hashes(line)
                if hash_rate:
                    self.actual_miner_vars['m_gpu']['works_ok'] = True
                    #self.insert_data(hash_rate,'m_gpu')
                    self.ddbb_insert_worker_stats(hash_rate,'m_gpu')
                    print str(hash_rate)
                else:
                    if self.actual_miner_vars['m_gpu']['works_ok'] == None and re.search(r'No device', line):
                        self.actual_miner_vars['m_gpu']['works_ok'] = False
                    print line    
        print 'monitor_bfgminer finished'

    
    def start_miner(self, miner_id):

        # we need to use id_miner to obtain miner_cmd from its shell script

        # miner_cmd = [
        #     '/home/hackturo/Software/miners/cpuminer-2.3.2/minerd',
        #     '-a',
        #     'sha256d',
        #     '-o',
        #     'stratum+tcp://stratum.bitcoin.cz:3333',
        #     '-O',
        #     'cloudminer.worker1:9868UyAN',
        #     ]
        
        currency = self.actual_miner_vars[miner_id]['currency']
        db_connection = pymongo.Connection('localhost', 27017)
        cloudminerDB = db_connection.cloudminerDB
        #col_status = cloudminerDB['col_status']
        col_active_miners = cloudminerDB['col_active_miners']
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        miner = {
            'id_worker': self.id_worker,
            'id_miner': miner_id,
            'currency': currency,
            'start_time' : timestamp,
            'start_time2' : ts,
            }

        col_active_miners.insert(miner)
        if not self.miner_cmds.has_key(miner_id):
            print 'unknown miner \"' + miner_id + '\", unable to start it'
            return
        self.actual_miner_vars[miner_id]['p_miner'] = subprocess.Popen(self.miner_cmds[miner_id], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.actual_miner_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_minerd)
        self.actual_miner_vars[miner_id]['t_monitor'].start()


    def test_miner(self, miner_id):
        if not self.miner_cmds.has_key(miner_id):
            print 'unknown miner \"' + miner_id + '\", unable to start it'
            return
        if miner_id=='m_cpu':
            self.actual_miner_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_minerd)
        elif miner_id=='m_gpu':
            self.actual_miner_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_bfgminer)
        self.actual_miner_vars[miner_id]['p_miner'] = subprocess.Popen(self.miner_cmds[miner_id], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.actual_miner_vars[miner_id]['t_monitor'].start()
        sleep(5)
        self.stop_miner(miner_id)
        if self.actual_miner_vars[miner_id]['works_ok']:
            print '\"' +miner_id+ '\" working OK!'
        else:
            print '\"' +miner_id+ '\" not runnable (check miner\'s help for more information)'
        self.delete_miner(miner_id)

    
    def delete_miner(self, miner_id):
        if self.actual_miner_vars.has_key(miner_id):
            del self.actual_miner_vars[miner_id]


    def delete_all_miners(self):
        for miner_id in self.actual_miner_vars:
            self.actual_miner_vars[miner_id].clear()
        self.actual_miner_vars.clear()
    
    
    def stop_miner(self, miner_id):
        if not self.actual_miner_vars.has_key(miner_id):
            print 'unknown miner \"' + miner_id + '\", unable to stop it'
            return
        if self.actual_miner_vars[miner_id]['p_miner'] != None:
            print 'Terminating the miner \''+ str(miner_id) + '\''
            db_connection = pymongo.Connection('localhost', 27017)
            cloudminerDB = db_connection.cloudminerDB
            col_active_miners = cloudminerDB['col_active_miners']
            miner = {
            'id_worker': self.id_worker,
            'id_miner': miner_id,
            }
            col_active_miners.remove(miner)
            if self.actual_miner_vars[miner_id]['p_miner'].poll() == None:
                self.actual_miner_vars[miner_id]['p_miner'].terminate()
            self.actual_miner_vars[miner_id]['t_monitor'].join(timeout=10)
            self.actual_miner_vars[miner_id]['p_miner'] = None
            self.actual_miner_vars[miner_id]['t_monitor'] = None
            print '\''+ str(miner_id) + '\' terminated'
            #self.delete_miner(miner_id)
        
    
    def stop_all_miners(self):
        for miner_id in self.actual_miner_vars:
            self.stop_miner(miner_id)

    
    def quit_server(self):
        self.invoker.handle_close()


    def execute_cmd(self, cmd):
        print str(cmd) + ' to be executed'
        opcode = str(cmd[0])
        if opcode == 'start' or opcode == 'test': #or opcode == 'stop':
            miner_id = str(cmd[1])
            self.actual_miner_vars[miner_id] = {'works_ok': None,
                                                'currency':'BTC',
                                                'p_miner':None,
                                                't_monitor':None}
            self.stop_miner(miner_id)
        if opcode == 'start':
            self.start_miner(miner_id)
        elif opcode == 'test':
            self.test_miner(miner_id)
        elif opcode == 'stop':
            miner_id = str(cmd[1])
            self.stop_miner(miner_id)
            self.delete_miner(miner_id)            
        elif opcode == 'quit':
            self.stop_all_miners()
            self.delete_all_miners()
            self.ddbb_remove_worker()
            self.quit_server()
        else:
            print 'Unknown Command'
