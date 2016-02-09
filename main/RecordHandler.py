# -*- coding: utf-8 -*-
__author__ = 'royyhma'


from PyQt4 import QtCore


#  功能与FileHandler类似
class RecordHandler:
    def __init__(self, name='newFile'):
        self.filename = name

    def setFileName(self, name='newFile'):
        self.filename = name

    def getFileName(self):
        return self.filename

    # 写入文件
    def writeFile(self, name, setting):
        myFile = QtCore.QFile(self.filename)
        if not(myFile.open(QtCore.QFile.ReadWrite | QtCore.QFile.Text | QtCore.QFile.Append)):
            print('Not able to write in this file')
            return
        outfile = QtCore.QTextStream(myFile)
        # 将文件写成 “文件名=信息”格式
        outfile << name << "=" << setting << "\n"
        myFile.flush()
        myFile.close()

    # 读取文件，并返回一个字典dict
    def readFile(self):
        myFile = QtCore.QFile(self.filename)
        if not(myFile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)):
            print('Not able to read this file')
            return
        dictionary = {}
        infile = QtCore.QTextStream(myFile)
        while not infile.atEnd():
            item = infile.readLine(100).split("=")
            dictionary[item[0]] = item[1]
        myFile.close()
        # 格式为：dictionary[文件名] = 信息
        return dictionary
