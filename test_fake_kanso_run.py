#!/usr/bin/env python
#-*- coding: utf-8 -*-

import fake_kanso

if __name__ == '__main__':
    fake_kanso.add_file('test_data/transactions', '/transactions')
    fake_kanso.add_file('test_data/outgoingTransactions', '/outgoingTransactions')
    fake_kanso.run()

    try:
        while 1:
            continue
    except KeyboardInterrupt:
        print "exit"
