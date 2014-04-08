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
import pymysql
import subprocess
import threading
import multiprocessing

class WorkerController(object):

    '''
    classdocs
    '''

    def __init__(self, invoker):
        '''
        Constructor
        '''
        self.invoker   = invoker
        
        self.conn_mysql = self.invoker.conn_mysql
        self.cur = self.conn_mysql.cursor()
        self.machine_DDBB_id = self.invoker.machine_DDBB_id
        self.platform_DDBB_id = self.invoker.platform_DDBB_id
        self.num_cpus = multiprocessing.cpu_count()
        
        self.actual_worker_vars = {} # empty two-level dictionary
        
        self.miner_cmds = {}
        self.miner_cmds['11232'] = [ #minerD Linux 32bit 2.3.2 version, BTC
                #'../Miners/minerd',
                '../Miners/11232/11232',
                '-a',
                'sha256d',
                '--benchmark'
                ]
        
        self.miner_cmds['21xxx'] = [    #BFGminer Linux 32bit/64bit x.x.x version, BTC 
                'bfgminer',             #(previously installed through PPA)
                '--benchmark',
                '--real-quiet'
                ]

        self.miner_cmds['23309'] = [ #BFGminer Win 32bit 3.0.9 version, BTC
                #'bfgminer',
                '../Miners/23309/23309.exe',
                '--benchmark',
                '--real-quiet'
                ]

        self.miner_cmds['24340'] = [ #BFGminer Win 64bit 3.4.0 version, BTC
                #'bfgminer',
                '../Miners/24340/24340.exe',
                '--benchmark',
                '--real-quiet'
                ]

        #print 'Worker: ' + self.id_worker
        #print 'Platform: ' + self.platform
        #print 'Is 64 bits: ' + str(self.is64bits)
        print 'Controller created'
        print ''
        
#         miner_id = 1
#         
#         self.test_miner(miner_id)
#         
#         self.start_miner(miner_id)
#         sleep(5)
#         self.stop_all_workers()

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

    
    def monitor_minerd(self, worker_id):
        num_lines = 0
        hash_rate = 0.0  # MH/s
        
        #while self.actual_worker_vars['11232']['p_miner'].poll() == None:
        while self.actual_worker_vars[worker_id]['p_miner'].poll() == None:
            #line = self.actual_worker_vars['11232']['p_miner'].stdout.readline()
            line = self.actual_worker_vars[worker_id]['p_miner'].stdout.readline()
            if line:
                line_hashes = self.parse_hashes(line)
                
                if line_hashes:
                    #self.actual_worker_vars['11232']['works_ok'] = True
                    self.actual_worker_vars[worker_id]['works_ok'] = True
                    hash_rate += line_hashes
                    num_lines += 1
                    #num_lines %= 4
                    num_lines %= self.num_cpus
                    if num_lines == 0:
                        #self.insert_data(hash_rate,'m_cpu')
                        #self.ddbb_insert_worker_stats(hash_rate,'11232')
                        self.ddbb_insert_worker_stats(hash_rate,worker_id)
                        print str(hash_rate)
                        hash_rate = 0  # reset hash count
                else:
                    #if self.actual_worker_vars['11232']['works_ok'] == None and re.search(r'Try', line):
                    if self.actual_worker_vars[worker_id]['works_ok'] == None and re.search(r'Try', line):
                        #self.actual_worker_vars['11232']['works_ok'] = False
                        self.actual_worker_vars[worker_id]['works_ok'] = False
                    print line

            # monitoring time
            # time.sleep(3)

        print 'monitor_minerd finished'

    def monitor_bfgminer(self):
        while self.actual_worker_vars['21xxx']['p_miner'].poll() == None:
            line = self.actual_worker_vars['21xxx']['p_miner'].stdout.readline()
            if line:
                hash_rate = self.parse_hashes(line)
                if hash_rate:
                    self.actual_worker_vars['21xxx']['works_ok'] = True
                    #self.insert_data(hash_rate,'21xxx')
                    self.ddbb_insert_worker_stats(hash_rate,'21xxx')
                    print str(hash_rate)
                else:
                    if self.actual_worker_vars['21xxx']['works_ok'] == None and re.search(r'No device', line):
                        self.actual_worker_vars['21xxx']['works_ok'] = False
                    print line    
        print 'monitor_bfgminer finished'

    
    def ddbb_insert_worker(self, miner_id):
        if(self.machine_DDBB_id!=None):
            ts = time.time()
            ts2 = str(datetime.datetime.fromtimestamp(ts))
            ts3 = ts2[0:ts2.find('.')]
            query = "INSERT INTO worker (machine_id, miner_id, time_start) VALUES (" \
                        + str(self.machine_DDBB_id) + "," \
                        + str(miner_id) + "," \
                        + "'" + ts3 + "');"
            self.cur.execute(query)
            self.conn_mysql.commit()
            
            #self.worker_DDBB_id = -1
            worker_id = -1
            query = "SELECT id FROM worker WHERE " \
                        + "machine_id = " + str(self.machine_DDBB_id) \
                        + " AND miner_id = " + str(miner_id) \
                        + " AND time_start = '" + ts3 + "';"
            self.cur.execute(query)
            for row in self.cur:
                #if(self.worker_DDBB_id == -1):
                if(worker_id == -1):
                    #self.worker_DDBB_id = row[0]
                    worker_id = row[0]
            #print 'Item inserted!!! (worker_id=' , self.worker_DDBB_id , ')'
            print 'Item inserted!!! (worker_id=' , worker_id , ')'
            return worker_id
        else:
            print '\'machine_id\' not set!! (cannot insert a new worker in DDBB)' 
            return None


    def ddbb_insert_worker_old(self):
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


    def ddbb_remove_worker(self, worker_id):
        if(worker_id!=None):
            ts = time.time()
            ts2 = str(datetime.datetime.fromtimestamp(ts))
            ts3 = ts2[0:ts2.find('.')]
            query = "UPDATE worker SET time_stop = '" + ts3 + "' WHERE id = " + str(worker_id) +";"
            self.cur.execute(query)
            self.conn_mysql.commit()
        else:
            print '\'worker_id\' not set!! (cannot remove worker from activity in DDBB)'


    def ddbb_remove_worker_old(self):
        db_connection = pymongo.Connection('localhost', 27017)
        cloudminerDB = db_connection.cloudminerDB
        #col_status = cloudminerDB['col_status']
        col_active_workers = cloudminerDB['col_active_workers']
        worker = {
            'id_worker': self.id_worker,
            }

        col_active_workers.remove(worker)


    def ddbb_insert_worker_stats(self, hash_rate, worker_id):
        if(worker_id != None and hash_rate != None):
            ts = time.time()
            ts2 = str(datetime.datetime.fromtimestamp(ts))
            ts3 = ts2[0:ts2.find('.')]
            query = "INSERT INTO worker_stats (worker_id, hash_rate, timestamp) VALUES (" \
                        + str(worker_id) + "," \
                        + str(hash_rate) + "," \
                        + "'" + ts3 + "');"
            
            self.cur.execute(query)
            self.conn_mysql.commit()
            print 'Item inserted!!!'
        else:
            print 'incorrect values (cannot insert new worker_stats in DDBB)' 
        

    def ddbb_insert_worker_stats_old(self, hash_rate, miner_id):
    #def insert_data(self, hash_rate, miner_id):
        #currency = self.actual_worker_vars[miner_id]['currency']
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

    def ddbb_get_miner_name(self, miner_id):
        if(miner_id != None):
            miner_name = None
            query = "SELECT name FROM miner WHERE id = " + str(miner_id) +";"
            self.cur.execute(query)
            for row in self.cur:
                if(miner_name == None):
                    miner_name = row[0]
            return miner_name
        else:
            print ' <ERROR> unknown miner_id while getting cmd_line from DDBB'
        

    def ddbb_get_miner_cmd_line(self, miner_id):
        if(miner_id != None):
            cmd_line = None
            query = "SELECT command_line FROM miner WHERE id = " + str(miner_id) +";"
            self.cur.execute(query)
            for row in self.cur:
                if(cmd_line == None):
                    cmd_line = row[0]
            return cmd_line
        else:
            print ' <ERROR> unknown miner_id while getting cmd_line from DDBB'
        

    def ddbb_get_miner_currency(self, miner_id):
        if(miner_id != None):
            currency = None
            query = "SELECT C.name FROM miner M, currency C WHERE " \
                        + " M.id = " + str(miner_id) \
                        + " AND M.currency_id = C.id;"
            self.cur.execute(query)
            for row in self.cur:
                if(currency == None):
                    currency = row[0]
            return currency
        else:
            print ' <ERROR> unknown miner_id while getting currency from DDBB'
        

    def add_worker(self, miner_id):
        if (miner_id == None):
            print ' <ERROR> unknown miner, unable to test it'
            return None
        
        worker_id = self.ddbb_insert_worker(miner_id)
        if (worker_id == None):
            print ' <ERROR> worker not inserted in DDBB, unable to test miner'
            return None
        
        cmd_line = self.ddbb_get_miner_cmd_line(miner_id)
        miner_name = self.ddbb_get_miner_name(miner_id)
        currency = self.ddbb_get_miner_currency(miner_id)
        if(cmd_line == None or miner_name == None or currency == None):
            print ' <ERROR> miner not found in DDBB, cannot add to dict'
            return None
        
        #self.actual_worker_vars[miner_id] = {'miner_name': miner_name,
        self.actual_worker_vars[worker_id] = {'miner_id': miner_id,
                                             'miner_name': miner_name,
                                             'works_ok':   None,
                                             'currency':   currency,
                                             'p_miner':    subprocess.Popen(cmd_line.split(), shell=False, \
                                                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT),
                                             't_monitor':  None}
        
        #if miner_id=='11232':
        if miner_name=='minerd':
            self.actual_worker_vars[worker_id]['t_monitor'] = threading.Thread(target=self.monitor_minerd, args=(worker_id,))
        #elif miner_id=='21xxx':
        elif miner_name=='bfgminer':
            self.actual_worker_vars[worker_id]['t_monitor'] = threading.Thread(target=self.monitor_bfgminer, args=(worker_id,))
        #self.actual_worker_vars[miner_id]['p_miner'] = subprocess.Popen(self.miner_cmds[miner_id], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #self.actual_worker_vars[miner_id]['p_miner'] = subprocess.Popen(cmd_line.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return worker_id
        
        
    def test_worker(self, miner_id):
        if (miner_id == None):
            print ' <ERROR> unknown miner, unable to test it'
            return None
        worker_id = self.add_worker(miner_id)
        if(worker_id == None):
            print ' <ERROR> miner variables not set in dict, unable to test it'
            return None
        
        #self.ddbb_insert_worker(miner_id)
        self.actual_worker_vars[worker_id]['t_monitor'].start()
        sleep(5)
        self.stop_worker(worker_id)
        if self.actual_worker_vars[worker_id]['works_ok']:
            print '\"' , self.actual_worker_vars[worker_id]['miner_name'] , '\" working OK!'
        else:
            print '\"' , self.actual_worker_vars[worker_id]['miner_name'] , '\" not runnable (check miner\'s help for more information)'
        self.delete_worker(worker_id)
        #self.ddbb_remove_worker(worker_id)
    
    def test_miner_old(self, miner_id):
        if not self.miner_cmds.has_key(miner_id):
            print 'unknown miner \"' + miner_id + '\", unable to start it'
            return
        #if miner_id=='m_cpu':
        if miner_id=='11232':
            self.actual_worker_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_minerd)
        #elif miner_id=='m_gpu':
        elif miner_id=='21xxx':
            self.actual_worker_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_bfgminer)
        self.actual_worker_vars[miner_id]['p_miner'] = subprocess.Popen(self.miner_cmds[miner_id], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.actual_worker_vars[miner_id]['t_monitor'].start()
        sleep(5)
        self.stop_miner(miner_id)
        if self.actual_worker_vars[miner_id]['works_ok']:
            print '\"' +miner_id+ '\" working OK!'
        else:
            print '\"' +miner_id+ '\" not runnable (check miner\'s help for more information)'
        self.delete_miner(miner_id)

    
    def start_worker(self, miner_id):
        # we need to use id_miner to obtain miner_cmd from its shell script
        if (miner_id == None):
            print ' <ERROR> unknown miner, unable to start it'
            return None
        worker_id = self.add_worker(miner_id)
        if(worker_id == None):
            print ' <ERROR> miner variables not set in dict, unable to start it'
            return None
        self.actual_worker_vars[worker_id]['t_monitor'].start()


    def start_miner_old(self, miner_id):

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
        currency = self.actual_worker_vars[miner_id]['currency']
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
        self.actual_worker_vars[miner_id]['p_miner'] = subprocess.Popen(self.miner_cmds[miner_id], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #if miner_id=='m_cpu':
        if miner_id=='11232':
            self.actual_worker_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_minerd)
        #elif miner_id=='m_gpu':
        elif miner_id=='21xxx':
            self.actual_worker_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_bfgminer)
        #self.actual_worker_vars[miner_id]['t_monitor'] = threading.Thread(target=self.monitor_minerd)
        self.actual_worker_vars[miner_id]['t_monitor'].start()


    def delete_worker(self, worker_id):
        if self.actual_worker_vars.has_key(worker_id):
            del self.actual_worker_vars[worker_id]


    def delete_all_workers(self):
        for worker_id in self.actual_worker_vars:
            self.actual_worker_vars[worker_id].clear()
        self.actual_worker_vars.clear()
    
    
    def stop_worker(self, worker_id):
        if self.actual_worker_vars.has_key(worker_id) and self.actual_worker_vars[worker_id]['p_miner'] != None:
            print 'Terminating the worker \''+ self.actual_worker_vars[worker_id]['miner_name'] + '\'' + str(worker_id)
            if self.actual_worker_vars[worker_id]['p_miner'].poll() == None:
                self.actual_worker_vars[worker_id]['p_miner'].terminate()
            self.actual_worker_vars[worker_id]['t_monitor'].join(timeout=10)
            self.actual_worker_vars[worker_id]['p_miner'] = None
            self.actual_worker_vars[worker_id]['t_monitor'] = None
            print '\''+ self.actual_worker_vars[worker_id]['miner_name'] + '\' terminated'
            self.ddbb_remove_worker(worker_id)
#             self.delete_worker(worker_id)
        else:
            print ' <ERROR> unknown worker \"' , worker_id , '\", unable to stop it'
            return
        
    
    def stop_miner_old(self, miner_id):
        if not self.actual_worker_vars.has_key(miner_id):
            print 'unknown miner \"' + miner_id + '\", unable to stop it'
            return
        if self.actual_worker_vars[miner_id]['p_miner'] != None:
            print 'Terminating the miner \''+ str(miner_id) + '\''
            db_connection = pymongo.Connection('localhost', 27017)
            cloudminerDB = db_connection.cloudminerDB
            col_active_miners = cloudminerDB['col_active_miners']
            miner = {
            'id_worker': self.id_worker,
            'id_miner': miner_id,
            }
            col_active_miners.remove(miner)
            if self.actual_worker_vars[miner_id]['p_miner'].poll() == None:
                self.actual_worker_vars[miner_id]['p_miner'].terminate()
            self.actual_worker_vars[miner_id]['t_monitor'].join(timeout=10)
            self.actual_worker_vars[miner_id]['p_miner'] = None
            self.actual_worker_vars[miner_id]['t_monitor'] = None
            print '\''+ str(miner_id) + '\' terminated'
            #self.delete_miner(miner_id)
        
    
    def stop_all_workers(self):
        for worker_id in self.actual_worker_vars:
            self.stop_worker(worker_id)

    
    def quit_server(self):
        self.invoker.handle_close()

    
    def quit(self):
        self.stop_all_workers()
        self.delete_all_workers()
#         self.ddbb_remove_worker()
        self.quit_server()
        
    
    def execute_cmd(self, cmd):
        print str(cmd) + ' to be executed'
        opcode = str(cmd[0])
        if opcode == 'start' or opcode == 'test': #or opcode == 'stop':
            miner_id = str(cmd[1])
#             self.actual_worker_vars[miner_id] = {'works_ok': None,
#                                                 'currency':'BTC',
#                                                 'p_miner':None,
#                                                 't_monitor':None}
#             self.stop_miner(miner_id)
        if opcode == 'start':
#             self.ddbb_insert_worker(miner_id)
            self.start_worker(miner_id)
        elif opcode == 'test':
            self.test_worker(miner_id)
        elif opcode == 'stop':
            worker_id = int(cmd[1])
            self.stop_worker(worker_id)
            self.delete_worker(worker_id)            
        elif opcode == 'quit':
            self.stop_all_workers()
            self.delete_all_workers()
#             self.ddbb_remove_worker()
            self.quit_server()
        else:
            print 'Unknown Command'

