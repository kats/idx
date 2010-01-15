#!/usr/bin/env python
#-*- coding: utf-8 -*-

from datetime import datetime
from os import listdir, remove, makedirs
from os.path import join, isfile, isdir
from re import compile, match
from shutil import copyfile

def getFileSuffix(dt):
    return dt.strftime('%Y-%m-%d-%H-%M-%S-%f')

class SnapshotError(Exception): pass

class Snapshot:
    def __init__(self, srcDir, fileName, dstDir):
        if not isdir(srcDir):
            raise SnapshotError('Source Directory does not exists: %s' % srcDir)
        self.__srcpath = join(srcDir, fileName)
        if not isfile(self.__srcpath):
            raise SnapshotError('Source file does not exists: "%s"' % self.__srcpath)
        self.__srcDir = srcDir
        self.__fileName = fileName
        self.__dstDir = dstDir
        if not isdir(self.__dstDir):
            makedirs(self.__dstDir)
        self.__snapshotFile = compile(self.__fileName.replace('.', '\.') + '\.\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{6}')

    def __dstFileName(self):
        return join(self.__dstDir, self.__fileName) + '.' + \
            getFileSuffix(datetime.now())

    def create(self):
        copyfile(self.__fileName, self.__dstFileName())

    def latestFilePath(self):
        names = listdir(self.__dstDir)
        names.sort()
        for i in xrange(len(names)-1, -1, -1):
            srcname = join(self.__dstDir, names[i])
            if self.__snapshotFile.match(names[i]):
                return srcname; 

    def replaceWithLatest(self):
        latest = self.latestFilePath()
        if not latest:
            return
        copyfile(latest, self.__srcpath)
        return latest

    def remove(snapshotName):
        if isfile(snapshotName):
            remove(snapshotName)

