#!/usr/bin/env python
#-*- coding: utf-8 -*-

import config

from datetime import datetime
from os import listdir, remove, makedirs
from os.path import join, isfile, isdir
from re import compile, match
from shutil import copyfile
from time import time

from index import PfrIndex

from logging import getLogger
log = getLogger('snapshot')

def getFileSuffix(dt):
    return dt.strftime('%Y-%m-%d-%H-%M-%S-%f')

class SnapshotError(Exception): pass

class Snapshot:
    def __init__(self, srcDir='.', fileName=config.IDX_FILENAME, dstDir=config.IDX_SNAPSHOT_DIR):
        if not isdir(srcDir):
            raise SnapshotError('Source Directory does not exists: %s' % srcDir)
        self.__srcpath = join(srcDir, fileName)
        self.__srcDir = srcDir
        self.__fileName = fileName
        self.__dstDir = dstDir
        if not isdir(self.__dstDir):
            makedirs(self.__dstDir)
        self.__snapshotFile = compile(self.__fileName.replace('.', '\.') + '\.\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{6}')
        self.__t = int(time()) + config.IDX_SNAPSHOT_PERIOD

    def __dstFileName(self):
        return join(self.__dstDir, self.__fileName) + '.' + \
            getFileSuffix(datetime.now())

    def create(self):
        if not isfile(self.__srcpath):
            raise SnapshotError('Source file does not exists: "%s"' % self.__srcpath)
        dst = self.__dstFileName()
        copyfile(self.__fileName, dst)
        res = PfrIndex(dst).validate()
        if not res:
            self.__remove(dst)
        else:
            self.__t = int(time())
            log.info('created:"%s"' % dst)
        self.__cleanup()
        return res

    def __cleanup(self):
        names = listdir(self.__dstDir)
        names.sort()
        c = 0
        for i in xrange(len(names)-1, -1, -1):
            srcname = join(self.__dstDir, names[i])
            if self.__snapshotFile.match(names[i]):
                c += 1
                if c > config.IDX_SNAPSHOT_MAX:
                    self.__remove(srcname)

    def __remove(self, snapshotName):
        if isfile(snapshotName):
            remove(snapshotName)
            log.info('removed:"%s"' % snapshotName)

    def isTime(self):
        return int(time()) > self.__t

    def restore(self, IndexClass):
        names = listdir(self.__dstDir)
        names.sort()
        for i in xrange(len(names)-1, -1, -1):
            n = join(self.__dstDir, names[i])
            if self.__snapshotFile.match(names[i]):
                idx = IndexClass(n)
                if idx.validate():
                    if isfile(self.__srcpath): self.__remove(self.__srcpath)
                    if isfile(n):
                        copyfile(n, self.__srcpath)
                        log.info('restored:%s' % n)
                        return True
        return False
