# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from PyQt4 import QtCore
from Queue import Queue
from uploader import Uploader
from RecordHandler import RecordHandler


class UploadingThread(QtCore.QThread):
    def __init__(self, number, direcotry, q=Queue(), fail_record={}):
        super(UploadingThread, self).__init__()
        # 记录自己的线程号
        self.thread_number = number
        # 初始化线程停止控制
        self.is_stop = False
        # 从user_info中读取记录
        self.info_ini = QtCore.QSettings("userinfo.ini", QtCore.QSettings.IniFormat)
        app_id = str(self.info_ini.value("/UserInfo/appID").toString())
        secret_id = str(self.info_ini.value("/UserInfo/secretID").toString())
        secret_key = str(self.info_ini.value("/UserInfo/secretKey").toString())
        bucket = str(self.info_ini.value("/UserInfo/bucket").toString())
        # 初始化上传模块
        self.up_agent = Uploader(app_id, secret_id, secret_key, bucket)
        # 初始化失败记录
        self.recorder = RecordHandler("fail")
        # 设置上传队列
        self.myq = q
        # 设置失败记录
        self.fail_record = fail_record
        # 设置一个目录控制器
        self.dir = QtCore.QDir(direcotry)

    def run(self):
        # 当传输队列里有货的的时候

        while not self.myq.empty():

            # 创建一个线程锁，防止多个线程同时处理一个资源
            mutex = QtCore.QMutex()
            # 上锁
            mutex.lock()
            print "There are %d item(s) left" % self.myq.qsize()
            if self.is_stop:
                break
            # 获取上传资源
            item = self.myq.get()
            # 发出上传信息，View应该将状态改为uploading...
            self.emit(QtCore.SIGNAL("started(QString)"), item)
            # 打印上传信息
            print("Thread%d is uploading " % self.thread_number + item)
            absolute_path = str(item)
            relative_path = self.dir.relativeFilePath(item)
            print "relative path is " + relative_path
            try:
                obj = self.up_agent.upload(absolute_path, relative_path)
                # self.sleep(2)
                # 发出完成信息，View应该将该单位消除
                if obj['httpcode'] == 200:
                    self.emit(QtCore.SIGNAL("uploaded(QString)"), item)
                    # 传输失败，记录失败信息
                else:
                    self.fail_record[item] = obj['message']
                    self.emit(QtCore.SIGNAL("failed(QString)"), item)
                # 发射更改进度条信息
                self.emit(QtCore.SIGNAL("progress_need_to_change(int)"), self.myq.qsize())
                # 文件名错误处理
            except TypeError:
                self.fail_record[item] = u"文件名错误"
                self.emit(QtCore.SIGNAL("failed(QString)"), item)
            # 解锁
            mutex.unlock()
