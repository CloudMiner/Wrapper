#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 25/10/2013

@authors: Arturo Pareja Garcia, Juan Arratia, Tomas Restrepo Klinge
'''

import re
import sys
import time
import datetime
from time import sleep

import pymysql
import subprocess
import threading
import multiprocessing
from time import sleep
import atexit
import logging
import sys
#import time
import os
import platform


def ddbb_insert_worker_stats( hash_rate, avg_hash_rate, hash_rate_count, worker_id):
    if(worker_id != None and hash_rate != None and avg_hash_rate != None and hash_rate_count != None):
        ts = time.time()
        ts2 = str(datetime.datetime.fromtimestamp(ts))
        ts3 = ts2[0:ts2.find('.')]
        query = "INSERT INTO worker_stats (worker_id, hash_rate, hash_avg, hash_count, timestamp) VALUES (" \
                    + str(worker_id) + "," \
                    + str(hash_rate) + "," \
                    + str(avg_hash_rate) + "," \
                    + str(hash_rate_count) + "," \
                    + "'" + ts3 + "');"
        
        self.cur.execute(query)
        self.conn_mysql.commit()
        print 'Item inserted!!!'
    else:
        print 'incorrect values (cannot insert new worker_stats in DDBB)' 










if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s')

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    local_ip = (s.getsockname()[0])
    s.close()
    address_server = (local_ip, 0)
    w = WorkerNode(address_server)
    atexit.register(exit_handler, w)
    
    



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
        print 'Controller created'
        print ''
        
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
        
        while self.actual_worker_vars[worker_id]['p_miner'].poll() == None:
            line = self.actual_worker_vars[worker_id]['p_miner'].stdout.readline()
            if line:
                line_hashes = self.parse_hashes(line)
                
                if line_hashes:
                    self.actual_worker_vars[worker_id]['works_ok'] = True
                    hash_rate += line_hashes
                    num_lines += 1
                    #num_lines %= 4
                    num_lines %= self.num_cpus
                    if num_lines == 0:
                        hash_and_count = self.ddbb_get_avg_hash_rate(worker_id)
                        if(hash_and_count != (None,None)):
                            count = hash_and_count[1]
                            avg_hash_rate = ((hash_and_count[0]*count)+hash_rate)/(count+1)
                            count += 1 
                            self.ddbb_insert_worker_stats(hash_rate,avg_hash_rate,count,worker_id)
                        else:
                            print '<ERROR> Unable to retrieve avg_hash_rate and count'
                        print str(hash_rate)
                        hash_rate = 0  # reset hash count
                else:
                    if self.actual_worker_vars[worker_id]['works_ok'] == None and re.search(r'Try', line):
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
            
            worker_id = -1
            query = "SELECT id FROM worker WHERE " \
                        + "machine_id = " + str(self.machine_DDBB_id) \
                        + " AND miner_id = " + str(miner_id) \
                        + " AND time_start = '" + ts3 + "';"
            self.cur.execute(query)
            for row in self.cur:
                if(worker_id == -1):
                    worker_id = row[0]
            if(worker_id == -1):
                print '<ERROR> unable insert the new worker in the DDBB (miner_id =', miner_id, ')' 
                return None
            else:
                print 'Item inserted!!! (worker_id=' , worker_id , ')'
                return worker_id
        else:
            print '\'machine_id\' not set!! (cannot insert a new worker in DDBB)' 
            return None


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


    def ddbb_insert_worker_stats(self, hash_rate, avg_hash_rate, hash_rate_count, worker_id):
        if(worker_id != None and hash_rate != None and avg_hash_rate != None and hash_rate_count != None):
            ts = time.time()
            ts2 = str(datetime.datetime.fromtimestamp(ts))
            ts3 = ts2[0:ts2.find('.')]
            query = "INSERT INTO worker_stats (worker_id, hash_rate, hash_avg, hash_count, timestamp) VALUES (" \
                        + str(worker_id) + "," \
                        + str(hash_rate) + "," \
                        + str(avg_hash_rate) + "," \
                        + str(hash_rate_count) + "," \
                        + "'" + ts3 + "');"
            
            self.cur.execute(query)
            self.conn_mysql.commit()
            print 'Item inserted!!!'
        else:
            print 'incorrect values (cannot insert new worker_stats in DDBB)' 
        

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
        

    def ddbb_get_avg_hash_rate(self, worker_id):
        if (worker_id != None):
            avg_hash = None
            count = None
            query = "SELECT t0.hash_avg, t0.hash_count " \
                    + "FROM worker_stats t0 " \
                    + "WHERE t0.worker_id = " + str(worker_id) \
                        + " AND t0.timestamp = (SELECT MAX(t1.timestamp) " \
                                            +" FROM worker_stats t1 " \
                                            + "WHERE t0.worker_id=t1.worker_id); "
            #print query
            self.cur.execute(query)
            for row in self.cur:
                if(avg_hash == None):
                    avg_hash = row[0]
                    count = row[1]
            return (avg_hash,count)
        else:
            print ' <ERROR> Unable to calculate avg hash_rate'
            return None
        
    def ddbb_check_working(self,worker_id):
        if (worker_id != None):
            hash_rate = None
            query = "SELECT t0.hash_rate " \
                    + "FROM worker_stats t0 " \
                    + "WHERE t0.worker_id = " + str(worker_id) \
                        + " AND t0.timestamp = (SELECT MAX(t1.timestamp) " \
                                            +" FROM worker_stats t1 " \
                                            + "WHERE t0.worker_id=t1.worker_id); "
            #print query
            self.cur.execute(query)
            for row in self.cur:
                if(hash_rate == None):
                    hash_rate = row[0]
            if hash_rate > 0:
                query =  "UPDATE worker " \
                        + "SET tested = 'T'" \
                        + "WHERE id = " + str(worker_id) + ";"
            else:
                query =  "UPDATE worker " \
                        + "SET tested = 'F'" \
                        + "WHERE id = " + str(worker_id) + ";"
            self.cur.execute(query)
        else:
            print ' <WARNING> Unable to check if worker is working properly (worker_id =', str(worker_id), ')'
            return None

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
        
        self.actual_worker_vars[worker_id] = {'miner_id': miner_id,
                                             'miner_name': miner_name,
                                             'works_ok':   None,
                                             'currency':   currency,
                                             'p_miner':    subprocess.Popen(cmd_line.split(), shell=False, \
                                                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT),
                                             't_monitor':  None}
        
        if miner_name=='minerd':
            self.actual_worker_vars[worker_id]['t_monitor'] = threading.Thread(target=self.monitor_minerd, args=(worker_id,))
        elif miner_name=='bfgminer':
            self.actual_worker_vars[worker_id]['t_monitor'] = threading.Thread(target=self.monitor_bfgminer, args=(worker_id,))
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
    
    def start_worker(self, miner_id):
        # we need to use id_miner to obtain miner_cmd from its shell script
        if (miner_id == None):
            print ' <ERROR> unknown miner, unable to start it'
            return None
        worker_id = self.add_worker(miner_id)
        if(worker_id == None):
            print ' <ERROR> miner variables not set in dict, unable to start it'
            return None
        self.ddbb_insert_worker_stats(0, 0, 0, worker_id)
        self.actual_worker_vars[worker_id]['t_monitor'].start()
#         sleep(30)
#         self.ddbb_check_working(worker_id)


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
        if opcode == 'start' or opcode == 'test':
            miner_id = str(cmd[1])
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

