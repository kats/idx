#!/usr/bin/env python
#-*- coding: utf-8 -*-


import httplib

c = httplib.HTTPConnection('127.0.0.1:8092')
c.request('STOP', '')
