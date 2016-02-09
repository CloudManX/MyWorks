# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from PyQt4 import QtCore


class FileHandler:
    def __init__(self, name='newFile'):
        self.filename = name

    # 更新当前处理的文件名
    def setFileName(self, name='newFile'):
        self.filename = name

    # 获取当前处理的文件名
    def getFileName(self):
        return self.filename

    # 写入文件
    def writeFile(self, *inputs):
        myFile = QtCore.QFile(self.filename)
        if not(myFile.open(QtCore.QFile.ReadWrite | QtCore.QFile.Text | QtCore.QFile.Append)):
            print('Not able to write in this file')
            return
        outfile = QtCore.QTextStream(myFile)
        for key in inputs:
            outfile << key << '\n'
        myFile.flush()
        myFile.close()

    # 读取文件，返回一个行的list
    def readFile(self):
        myFile = QtCore.QFile(self.filename)
        if not(myFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)):
            print('Not able to read this file')
            return
        li = []
        infile = QtCore.QTextStream(myFile)
        while not infile.atEnd():
            item = infile.readLine(100)
            li.append(str(item))
        myFile.close()
        return li
