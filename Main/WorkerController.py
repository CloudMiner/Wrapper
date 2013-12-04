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
        self.id_worker = invoker.id_worker
        self.is64bits  = sys.maxsize > 2 ** 32
        self.platform  = sys.platform
        self.id_miner  = None
        self.currency_cpu  = None
        self.currency_gpu  = None
        self.p_miner_cpu   = None     # Miner Process on CPU
        self.p_miner_gpu   = None     # Miner Process on GPU
        self.t_monitor_cpu = None   # Monitor Thread
        self.t_monitor_gpu = None   # Monitor Thread
        self.miner_cpu_ok = None
        self.miner_gpu_ok = None

        print 'Worker: ' + self.id_worker
        print 'Platform: ' + self.platform
        print 'Is 64 bits: ' + str(self.is64bits)
        print 'Controller created'

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

    def insert_data(self, hash_rate, miner_id):
        if miner_id=='m_cpu':
            currency = self.currency_cpu
        elif miner_id=='m_gpu':
            currency = self.currency_gpu
        
        db_connection = pymongo.Connection('localhost', 27017)
        cloudminerDB = db_connection.cloudminerDB
        col_status = cloudminerDB['col_status']
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        status = {
            'id_worker': self.id_worker,
            #'id_miner': self.id_miner,
            'id_miner': miner_id,
            #'currency': self.currency,
            'currency': currency,
            'hash_rate': hash_rate,
            'datetime' : timestamp,
            'datetime2' : ts,
            }

        col_status.insert(status)
        print 'Item inserted!!!'

    def monitor_minerd(self):
        num_lines = 0
        hash_rate = 0  # MH/s
        while self.p_miner_cpu.poll() == None:
            line = self.p_miner_cpu.stdout.readline()

            if line:
                line_hashes = self.parse_hashes(line)
                
                if line_hashes:
                    self.miner_cpu_ok = True
                    hash_rate += line_hashes
                    num_lines += 1
                    num_lines %= 4
                    if num_lines == 0:
                        self.insert_data(hash_rate,'m_cpu')
                        print str(hash_rate)
                        hash_rate = 0  # reset hash count
                else:
                    if self.miner_cpu_ok == None and re.search(r'Try', line):
                        self.miner_cpu_ok = False
                    print line

            # monitoring time
            # time.sleep(3)

        print 'monitor_minerd finished'

    def monitor_bfgminer(self):
        while self.p_miner_gpu.poll() == None:
            line = self.p_miner_gpu.stdout.readline()
            if line:
                hash_rate = self.parse_hashes(line)
                if hash_rate:
                    self.miner_gpu_ok = True
                    self.insert_data(hash_rate,'m_gpu')
                    print str(hash_rate)
                else:
                    if self.miner_gpu_ok == None and re.search(r'No device', line):
                        self.miner_gpu_ok = False
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

        if miner_id=='m_cpu':
            miner_cmd = [
            #    '/home/hackturo/Software/miners/cpuminer-2.3.2/minerd',
                '../Miners/minerd',
                '-a',
                'sha256d',
                '--benchmark'
                ]
            self.p_miner_cpu = subprocess.Popen(miner_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #self.p_miner_cpu = subprocess.Popen('../Lanzadores/start_minerd_BTC_benchmark.sh', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.t_monitor_cpu = threading.Thread(target=self.monitor_minerd)
            self.t_monitor_cpu.start()
        elif miner_id=='m_gpu':
            miner_cmd = [
                'bfgminer',
                '--real-quiet',
                '--benchmark'
                ]
            self.p_miner_gpu = subprocess.Popen(miner_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #self.p_miner_gpu = subprocess.Popen('../Lanzadores/start_bfgminer_BTC_benchmark.sh', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.t_monitor_gpu = threading.Thread(target=self.monitor_bfgminer)
            self.t_monitor_gpu.start()

    def stop_miner(self, miner_id):
        if miner_id=='m_cpu':
            if self.p_miner_cpu != None:
                print 'Terminating the miner on cpu'
    
                if self.p_miner_cpu.poll() == None:
                    self.p_miner_cpu.terminate()
    
                self.t_monitor_cpu.join(timeout=10)
                self.p_miner_cpu = None
                self.t_monitor_cpu = None
                print 'CPU miner terminated'
        elif miner_id=='m_gpu':
            if self.p_miner_gpu != None:
                print 'Terminating the miner on gpu'
    
                if self.p_miner_gpu.poll() == None:
                    self.p_miner_gpu.terminate()
    
                self.t_monitor_gpu.join(timeout=10)
                self.p_miner_gpu = None
                self.t_monitor_gpu = None
                print 'GPU miner terminated'

    def test_miner(self, miner_id):
        if miner_id=='m_cpu':
            miner_cmd = [
            #    '/home/hackturo/Software/miners/cpuminer-2.3.2/minerd',
                '../Miners/minerd',
                '-a',
                'sha256d',
                '--benchmark'
                ]
            self.p_miner_cpu = subprocess.Popen(miner_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #self.p_miner_cpu = subprocess.Popen('../Lanzadores/start_minerd_BTC_benchmark.sh', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.t_monitor_cpu = threading.Thread(target=self.monitor_minerd)
            self.t_monitor_cpu.start()
            sleep(5)
            self.stop_miner(miner_id)
            if self.miner_cpu_ok:
                print 'minerD-cpuminer working OK!'
            else:
                print 'minerD-cpuminer not runnable (check miner\'s help for more information)'
        elif miner_id=='m_gpu':
            miner_cmd = [
                'bfgminer',
                '--real-quiet',
                '--benchmark'
                ]
            self.p_miner_gpu = subprocess.Popen(miner_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            #self.p_miner_gpu = subprocess.Popen('../Lanzadores/start_bfgminer_BTC_benchmark.sh', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            self.t_monitor_gpu = threading.Thread(target=self.monitor_bfgminer)
            self.t_monitor_gpu.start()
            sleep(5)
            self.stop_miner(miner_id)
            if self.miner_gpu_ok:
                print 'bfgminer working OK!'
            else:
                print 'bfgminer not runnable (probably GPU not usable for mining, check miner\'s help for more information)'
    
    def quit_server(self):
        self.invoker.handle_close()

    def execute_cmd(self, cmd):
        print str(cmd) + ' to be executed'
        opcode = str(cmd[0])
        if opcode == 'start' or opcode == 'test' or opcode == 'stop':
            #self.id_miner = str(cmd[1])
            self.currency_cpu = 'BTC'
            self.stop_miner(str(cmd[1]))
        if opcode == 'start':
            #self.id_miner = str(cmd[1])
            #self.currency_cpu = 'BTC'
            self.start_miner(str(cmd[1]))
        elif opcode == 'test':
            self.test_miner(str(cmd[1]))
        elif opcode == 'stop':
            pass
        #    self.stop_miner()
        elif opcode == 'quit':
            self.stop_miner('m_cpu')
            self.stop_miner('m_gpu')
            self.quit_server()
        else:
            print 'Unknown Command'
