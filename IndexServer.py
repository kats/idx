#!/usr/bin/env python
#-*- coding: utf-8 -*-

class IndexSearchResult:
    def __init__(self, data):
        self.data = data
    def __unicode__(self):
        return self.data
    def __str__(self):
        return self.__unicode__()

class IndexServer:
    def search(self, query):
        return [IndexSearchResult('field 1\tfield 2\tfield 3\tfield 4\n'), \
                IndexSearchResult('field 1\tfield 2\tfield 3\tfield 4\n'), \
                IndexSearchResult('field 1\tfield 2\tfield 3\tfield 4\n'), \
                IndexSearchResult('field 1\tfield 2\tfield 3\tfield 4\n')] 


