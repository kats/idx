#!/usr/bin/env python
#-*- coding: utf-8 -*-


from sqlite3 import connect
import config

#res = c.execute('select count(*) from pfrTransactions').fetchone()

if __name__ == '__main__':
    c = connect(config.IDX_FILENAME_STRINING)
    res = c.execute('PRAGMA integrity_check').fetchone()
    print res[0]
    print res[0] == 'ok'

    res = c.execute('PRAGMA table_info(pfrTransactions)').fetchall()
    print res
    r = res and len(res) == 13 and \
        res[0][1] == 'id' and \
        res[1][1].lower() == 'orgid_hi' and \
        res[2][1].lower() == 'orgid_low' and \
        res[3][1].lower() == 'dcid_hi' and \
        res[4][1].lower() == 'dcid_low' and \
        res[5][1].lower() == 'transactiontime' and \
        res[6][1].lower() == 'transactiontype' and \
        res[7][1].lower() == 'upfrcode' and \
        res[8][1].lower() == 'accountingyear' and \
        res[9][1].lower() == 'provideridhash' and \
        res[10][1].lower() == 'correctiontype' and \
        res[11][1].lower() == 'documents' and \
        res[12][1].lower() == 'signatures'
    print r

    res = c.execute('PRAGMA table_info(state)').fetchall()
    print res
    
    r = res and len(res) == 1 and \
        res[0][1] == 'offset'
    print r

    res = c.execute('PRAGMA index_info(pfrTransactions_index)').fetchall()
    print res

    r = res and len(res) == 2 and \
        res[0][2].lower() == 'orgid_hi' and \
        res[1][2].lower() == 'orgid_low'
    print r
    c.close()
