#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Created on 14/11/2013

@author: hackturo
'''

import re
import logging
import asyncore

from time import sleep
from TaskMaster import TaskMaster


def send_task(addr, task):
    print 'inicializa el TaskMaster'
    connector = TaskMaster(addr)
    print 'TaskMaster manda el comando: ' + str(task)
    connector.send_command(task)
    asyncore.loop()
    print 'CALLBACK:' + connector.get_callback()


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
            is_valid = True
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


def ask_command(address):
    cmd = ''
    cmd_menu = ['Start', 'Stop', 'Back']
    choice = query_input('CHOOSE A COMMAND', cmd_menu)
    if choice == 1:
        cmd = 'start BTC'
    elif choice == 2:
        cmd = 'stop'
    elif choice == 3:
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
            print 'You choose Send command'
            address = ask_address()
            if address != (None, None):
                go_back = False
                while not go_back:
                    go_back = ask_command(address) == 'Back'
        elif choice == 2:

            print 'You chooose View worker status'
            print 'Not available now... (sorry)'
        elif choice == 3:

            is_exit = True
            print 'Exiting...'
        else:

            print '[ERR] Invalid input number. Try again...'

    print 'bye.'
    sleep(3)
