#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 14/11/2013

@author: hackturo
'''

import re
import logging
import asyncore
import pymongo

from time import sleep
from TaskMaster import TaskMaster


def send_task(addr, task):
    print 'inicializa el TaskMaster'
    connector = TaskMaster(addr)
    print 'TaskMaster manda el comando: ' + str(task)
    connector.send_command(task)
    asyncore.loop()
    print 'CALLBACK:' + connector.get_callback()


def retrieve_data(worker_id):
    db_connection = pymongo.Connection('localhost', 27017)
    cloudminerDB = db_connection.cloudminerDB
    col_status = cloudminerDB['col_status']    
    cols = col_status.find({"id_worker":worker_id},{'datetime':1,'datetime2':1,'hash_rate':1,'_id':0}).sort("datetime2",-1)
    col = next(cols, None)
    if col:
        print "last online: "+col['datetime']#+"\n"
        print "hashing rate: "+str(col['hash_rate'])+" MH/s"
    else:
        print "No data for selected worker" 

def gen_separator():
    return 33 * '-'


def gen_options(opt):
    options = ''
    n = len(opt)
    for i in range(n):
        options += str(i + 1) + '. ' + opt[i]
        if i < n - 1:
            options += '\n'
    return options


def query_input(menu_title, options):
    n = len(options)
    choice = None
    is_valid = False
    while not is_valid:
        print gen_separator()
        print menu_title
        print gen_options(options)
        print gen_separator()
        try:
            choice = int(raw_input('Enter your choice [1-' + str(n)
                         + '] : '))
            is_valid = (choice >= 1 and choice <= n)
        except ValueError, e:
            print "'%s' is not a valid integer." % e.args[0].split(': '
                    )[1]
    return choice


def ask_address():
    ip = None
    port = None
    data = raw_input('Enter IPv4:Port [X.X.X.X:YYYYY] address:\n')
    if re.match('(\d{1,3}\.){3}\d{1,3}(:\d{1,5})', data):
        addr = data.split(':')
        ip = addr[0]
        port = int(addr[1])
    return (ip, port)

def ask_miner():
    miner_menu = ['minerd (cpuminer)', 'bfgminer', 'Back']
    choice = query_input('CHOOSE A MINER', miner_menu)
    if choice == 1:
        return 'm01'
    elif choice == 2:
        return 'm02'
    elif choice == 3:
        return 'Back'
    else:
        print '[ERR] Invalid miner...'

def ask_command(address):
    cmd = ''
    cmd_menu = ['Start worker', 'Stop worker', 'Terminate worker', 'Back']
    choice = query_input('CHOOSE A COMMAND', cmd_menu)
    if choice == 1:
        miner = ask_miner()
        if miner==None or miner=='Back':
            return None
        else:
            cmd = 'start '+miner
        #cmd = 'start BTC'
    elif choice == 2:
        cmd = 'stop'
    elif choice == 3:
        cmd = 'quit'
    elif choice == 4:
        return 'Back'
    else:
        print '[ERR] Invalid command...'
        return None

    send_task(address, cmd)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s')
    header = '  - C L O U D M I N E R -  '
    subtitle = '    Head Node v0.1 alpha    '
    main_menu = ['Send command', 'View status', 'Exit']

    print gen_separator()
    print header
    print subtitle

    is_exit = False
    while not is_exit:
        choice = query_input('MAIN MENU', main_menu)

        # Main Menu options

        if choice == 1:
            print 'You chose \'Send command\''
            address = ask_address()
            if address != (None, None):
                go_back = False
                while not go_back:
                    go_back = ask_command(address) == 'Back'
        elif choice == 2:
            print 'You chose \'View worker status\''
            worker = choice = raw_input('Enter worker\'s id: ')
            retrieve_data(worker)
            #print 'Not available now... (sorry)'
        elif choice == 3:

            is_exit = True
            print 'Exiting...'
        else:

            print '[ERR] Invalid input number. Try again...'

    print 'bye.'
    sleep(3)
