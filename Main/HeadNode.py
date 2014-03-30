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
import pymysql
import random

from time import sleep
from TaskMaster import TaskMaster


def send_task(addr, task):
    print 'inicializa el TaskMaster'
    connector = TaskMaster(addr)
    print 'TaskMaster manda el comando: ' + str(task)
    connector.send_command(task)
    asyncore.loop()
    print 'CALLBACK:' + connector.get_callback()

def ddbb_connection():
    return pymysql.connect(host='127.0.0.1', port=3306, user='clminer', passwd='cloudminer2014', db='cloudminer')

def ddbb_retrieve_workers_status():#worker_id):
    db_connection = pymongo.Connection('localhost', 27017)
    cloudminerDB = db_connection.cloudminerDB
    col_active_workers = cloudminerDB['col_active_workers']
    cols_w = col_active_workers.find().sort("start_time2",-1)
    for col_w in cols_w:
        print "\""+col_w['id_worker']+"\" (alive since: "+col_w['start_time']+") -->"
        col_active_miners = cloudminerDB['col_active_miners']    
        cols_m = col_active_miners.find({"id_worker":col_w['id_worker']}).sort("start_time2",-1)
        #col_m = next(cols_m, None)
        #if col_m:
        for col_m in cols_m:
            print "  - \""+col_m['id_miner']+"\" started at: "+col_m['start_time']
            print "    - currency:"+col_m['currency']
            col_worker_stats = cloudminerDB['col_worker_stats']
            cols_s = col_worker_stats.find({"id_worker":col_w['id_worker'],"id_miner":col_m['id_miner']}).sort("start_time2",-1)
            col_s = next(cols_s, None)
            if col_s:
                print "    - hashing rate: "+str(col_s['hash_rate'])+" MH/s" 

def ddbb_retrieve_connections():
    address_list = []
    conn_mysql = ddbb_connection()
    cur = conn_mysql.cursor()
    
    query = "SELECT * FROM machine WHERE alive = 'T'"
    cur.execute(query)
    
    struct = cur.description
    i = 0;
    id_idx = -1
    name_idx = -1
    ip_idx = -1
    port_idx = -1
    plat_id_idx = -1
    for s in struct:
#         print(s)
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
#         print id_idx , " -- " , name_idx , " -- " , ip_idx , " -- " , port_idx , " -- " , plat_id_idx
#         print ""
        pass
    else:
        print(" <ERROR> Unable to obtain data from cloudminer.platform...")
        return None
        #throw error and quit!!
            
    for row in cur:
#         print row[id_idx] , " -- " , row[name_idx] , " -- " , row[ip_idx] , " -- " , row[port_idx] , " -- " , row[plat_id_idx]
#         print ""
        if row[ip_idx]=='0.0.0.0':
            IP = '127.0.0.1'
        else:
            IP = row[ip_idx]
        address_list.append({'machine_id'  : row[id_idx],
                             'machine_name': row[name_idx],
                             'platform_id' : row[plat_id_idx],
                             'IP'          : IP,
                             'port'        : row[port_idx],
                             })    
    return address_list


def ddbb_retrieve_connections_old():
    address_list = []
    db_connection = pymongo.Connection('localhost', 27017)
    cloudminerDB = db_connection.cloudminerDB
    col_active_workers = cloudminerDB['col_active_workers']    
    #cols = col_status.find({"id_worker":worker_id},{'datetime':1,'datetime2':1,'hash_rate':1,'_id':0}).sort("datetime2",-1)
    cols = col_active_workers.find().sort("start_time2",-1)
    for col in cols:
        if col['IP']=='0.0.0.0':
            IP='127.0.0.1'
        else:
            IP=col['IP']
        address_list.append({'worker_id':col['id_worker'],
                        'IP':IP,
                        #'port':12345,
                        'port':col['port'],
                        })
    return address_list

'''def ddbb_retrieve_active_workers():
    db_connection = pymongo.Connection('localhost', 27017)
    cloudminerDB = db_connection.cloudminerDB
    col_status = cloudminerDB['col_status']    
    #cols = col_status.find({"id_worker":worker_id},{'datetime':1,'datetime2':1,'hash_rate':1,'_id':0}).sort("datetime2",-1)
    cols = col_status.find({"id_worker":worker_id}).sort("datetime2",-1)
    col = next(cols, None)
    if col:
        print "last online ("+col['id_miner']+"): "+col['datetime']#+"\n"
        print "hashing rate ("+col['id_miner']+"): "+str(col['hash_rate'])+" MH/s"
    else:
        print "No data for selected worker" '''


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
    first_time = True
    while not is_valid:
        if not first_time:
            print ' <ERR> Invalid option...'
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
        first_time = False
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


def ask_worker(machine_id):
    conn_mysql = ddbb_connection()
    cur = conn_mysql.cursor()
    
    query = "SELECT M.name AS miner, C.name, W.id AS currency " \
                +" FROM worker W, miner M, currency C " \
                +" WHERE W.machine_id = " + str(machine_id) \
                    +" AND W.time_stop IS NULL" \
                    +" AND W.miner_id = M.id" \
                    +" AND M.currency_id = C.id;"
    cur.execute(query)
    
    miner_menu = []
    worker_list = []
    for row in cur:
#         print row[id_idx] , " -- " , row[name_idx] , " -- " , row[ip_idx] , " -- " , row[port_idx] , " -- " , row[plat_id_idx]
#         print ""
        miner_menu.append(row[0]+" -- "+row[1]) 
        worker_list.append(row[2])
    
    #miner_menu = ['minerd (CPUminer)', 'bfgminer (GPU)', 'Back']
    if not miner_menu:
        print 'There are no alive machines at the moment...'
        print ''
        return 'Back'
    choice = query_input('CHOOSE A WORKER', miner_menu)
    if choice > 0 and choice <= len(miner_menu):
        return str(worker_list[choice-1])
    elif choice == len(miner_menu) + 1:
        return 'Back'
    else:
        print ' <ERR> Invalid worker...'
        
#     if choice == 1:
        #return 'm_cpu'
        #return '11232'
#         return '1'
#     elif choice == 2:
        #return 'm_gpu'
        #return '21xxx'
#         return '2'
#     elif choice == 3:
#         return 'Back'
#     else:
#         print ' <ERR> Invalid worker...'



def ask_miner():
    miner_menu = ['minerd (CPUminer)', 'bfgminer (GPU)', 'Back']
    choice = query_input('CHOOSE A MINER', miner_menu)
    if choice == 1:
        #return 'm_cpu'
        #return '11232'
        return '1'
    elif choice == 2:
        #return 'm_gpu'
        #return '21xxx'
        return '2'
    elif choice == 3:
        return 'Back'
    else:
        print ' <ERR> Invalid miner...'


def ask_command(address, machine_id):
    cmd = ''
    cmd_menu = ['Start miner', 'Stop miner', 'Test miner', 'Terminate worker', 'Back']
    choice = query_input('CHOOSE A COMMAND', cmd_menu)
    if choice == 1 or choice == 3: #or choice == 2 
        miner = ask_miner()
        if miner==None or miner=='Back':
            return None   
    if choice == 1:
        cmd = 'start '+ miner
        #cmd = 'start BTC'
    elif choice == 2:
        worker = ask_worker(machine_id)
        if worker==None or worker=='Back':
            return None
        cmd = 'stop ' + worker
    elif choice == 3:
        cmd = 'test ' + miner
    elif choice == 4:
        cmd = 'quit'
        #return 'Back'
    elif choice == 5:
        return 'Back'
    else:
        print '[ERR] Invalid command...'
        return None

    send_task(address, cmd)
    if choice == 4:
        return 'Back'

def ask_connection():
    connection_menu = []
    address_list = ddbb_retrieve_connections()
    if(len(address_list)<1):
        print 'There are no alive machines at the moment...'
        print ''
        return None
    else:
        for con in address_list:
            #connection_menu.append(con['worker_id']+' -> '+con['IP']+':'+str(con['port']))
            connection_menu.append(con['machine_name']+' -> '+con['IP']+':'+str(con['port']))
        connection_menu.append('Back')
        choice = query_input('CHOOSE A CONNECTION', connection_menu)
        #if choice == 1: # 'New connection option
        #    return 0
        #el
        if choice <= len(address_list): # valid connections option
            return choice
        elif choice == len(address_list): # 'Back' option
            return -1
        else:
            print ' <ERROR> Invalid option...'
            return None
    
'''
def ask_connection(address_list,ask_new):
    connection_menu = []
    if(ask_new):
        connection_menu.append('New connection...')
    for con in address_list:
        connection_menu.append(con['worker_id']+' -> '+con['IP']+':'+str(con['port']))
    connection_menu.append('Back')
    choice = query_input('CHOOSE A CONNECTION', connection_menu)
    if choice == 1: # 'New connection option
        return 0
    elif choice <= len(address_list)+1: # valid connections option
        return choice-1
    elif choice == len(address_list)+2: # 'Back' option
        return -1
    else:
        print '[ERR] Invalid option...'
        return None
'''
def ask_IP():
    ip = raw_input('Enter IPv4 [X.X.X.X] address:\n')
    if re.match('(\d{1,3}\.){3}\d{1,3}', ip):
        return ip
    else:
        print ' <ERROR> wrong format'
        return None

def ask_port():
    try:
        port = int(raw_input('Enter port (1-99999):\n'))
        if port>=1 and port<=99999:
            return port
        else:
            print ' <ERROR> number out of valid interval'
            return None
    except ValueError:
        print ' <ERROR> not a number'
        return None
    

def config_connection(connection_number, address_list):
    config_menu = ['Change IP', 'Change port', 'Close connection', 'Back']
    choice = query_input('CHOOSE AN ACTION', config_menu)
    if choice == 1:
        ip = ask_IP()
        while ip == None:
            ip = ask_IP()
        address_list[connection_number-1]['IP'] = ip
    elif choice == 2:
        port = ask_port()
        while port == None:
            port = ask_port()
        address_list[connection_number-1]['port'] = port
    elif choice == 3:
        address_list.pop(connection_number-1)
    elif choice == 4:
        #return 'Back'
        pass
    else:
        print ' <ERROR> Invalid command...'
        return None

if __name__ == '__main__':
    worker_configured = False
    '''address_list = [{'worker_id':'WORKER1',
                     'IP':'127.0.0.1',
                     'port':12345}]
    '''
    address_list = ddbb_retrieve_connections()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s: %(message)s')
    header = '  - C L O U D M I N E R -  '
    subtitle = '    Head Node v0.3 alpha    '
    #main_menu = ['Send command', 'View status', 'Exit']
    #if worker_configured:
    main_menu = ['Connections setup', 'Send command', 'View worker status', 'Exit']
    #else:
    #    main_menu = ['Connection setup', 'Exit']

    print gen_separator()
    print header
    print subtitle

    is_exit = False
    while not is_exit:
        choice = query_input('MAIN MENU', main_menu)

        # Main Menu options

        if choice == 1:
            #print 'You chose \'Connections setup\''
            print 'You chose \"'+ main_menu[0] +'\"'
            #connection_number = ask_connection(address_list,True)
            connection_number = ask_connection()
            if connection_number != None:
                if connection_number == 0:
                    address = ask_address()
                    while address == (None,None):
                        print '[ERR] wrong format'
                        address = ask_address()
                    print address
                    address_list.append({'worker_id':'WORKER'+str(random.randint(1,10)),
                                         'IP':address[0],
                                         'port':address[1]})
                elif connection_number != -1:
                    print connection_number
                    config_connection(connection_number, address_list)
        elif choice == 2:
            #print 'You chose \'Send command\''
            print 'You chose \"'+ main_menu[1] +'\"'
            #address = ask_address()
            #if address != (None, None):
            #if(len(address_list)>0):
                #connection_number = ask_connection(address_list,False)
            address_list = ddbb_retrieve_connections()
            connection_number = ask_connection()
            if connection_number != None and connection_number != -1: 
                address = (address_list[connection_number-1]['IP'],int(address_list[connection_number-1]['port']))
                print address
                #Probe destinatary to check if it is alive
                go_back = False
                while not go_back:
                    go_back = ask_command(address, address_list[connection_number-1]['machine_id']) == 'Back'
            #else:
            #    print 'No connections configured...'
        elif choice == 3:
            #print 'You chose \'View worker status\''
            print 'You chose \"'+ main_menu[2] +'\"'
            #worker = choice = raw_input('Enter worker\'s id: ')
            #ddbb_retrieve_worker_status(worker)
            #ddbb_retrieve_worker_status('WORKER1')
            ddbb_retrieve_workers_status()
        elif choice == 4:
            is_exit = True
            print 'Exiting...'
            
        else:
            print '[ERR] Invalid input number. Try again...'

    print 'bye.'
    sleep(3)
