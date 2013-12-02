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
        self.id_miner  = None
        self.currency  = None
        self.is64bits  = sys.maxsize > 2 ** 32
        self.platform  = sys.platform
        self.p_miner   = None     # Miner Process
        self.t_monitor = None   # Monitor Thread

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

    def insert_data(self, hash_rate):
        db_connection = pymongo.Connection('localhost', 27017)
        cloudminerDB = db_connection.cloudminerDB
        col_status = cloudminerDB['col_status']
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y %H:%M:%S')
        status = {
            'id_worker': self.id_worker,
            'id_miner': self.id_miner,
            'currency': self.currency,
            'hash_rate': hash_rate,
            'datetime' : timestamp,
            'datetime2' : ts,
            }

            # "datetime"  : datetime HAY QUE CALCULAR DATETIME

        col_status.insert(status)
        print 'Item inserted!!!'

    def monitor(self):
        num_lines = 0
        hash_rate = 0  # MH/s
        while self.p_miner.poll() == None:
            line = self.p_miner.stdout.readline()

            if line:
                line_hashes = self.parse_hashes(line)

                if line_hashes:
                    hash_rate += line_hashes
                    num_lines += 1
                    num_lines %= 4
                    if num_lines == 0:
                        self.insert_data(hash_rate)
                        print str(hash_rate)
                        hash_rate = 0  # reset hash count
                else:
                    print line

            # monitoring time
            # time.sleep(3)

        print 'monitor finished'

    def start_miner(self):

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

        miner_cmd = [
            '/home/hackturo/Software/miners/cpuminer-2.3.2/minerd',
            '--benchmark'
            ]
        #self.p_miner = subprocess.Popen(miner_cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        #self.p_miner = subprocess.Popen('../Lanzadores/start_minerd_BTC_slush_worker1.sh', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.p_miner = subprocess.Popen('../Lanzadores/start_minerd_BTC_benchmark.sh', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.t_monitor = threading.Thread(target=self.monitor)
        self.t_monitor.start()

    def stop_miner(self):
        if self.p_miner != None:
            print 'Terminating the miner'

            if self.p_miner.poll() == None:
                self.p_miner.terminate()

            self.t_monitor.join(timeout=10)
            self.p_miner = None
            self.t_monitor = None

            print 'Miner terminated'

    def quit_server(self):
        self.invoker.handle_close()

    def execute_cmd(self, cmd):
        print str(cmd) + ' to be executed'
        opcode = str(cmd[0])

        if opcode == 'start':
            self.stop_miner()
            self.id_miner = str(cmd[1])
            self.currency = 'BTC'
            self.start_miner()
        elif opcode == 'stop':
            self.stop_miner()
        elif opcode == 'quit':
            self.stop_miner()
            self.quit_server()
        else:
            print 'Unknown Command'
