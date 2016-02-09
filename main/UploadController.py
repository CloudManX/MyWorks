# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from Queue import Queue
from UploadingThread import UploadingThread


# 上传控制器
class UploadController:
    def __init__(self, fail_record, directory):
        # 初始化上传队列
        self.upload_list = Queue()
        # 初始化线程List
        self.threads = []
        # 继承失败记录
        self.fail_record = fail_record
        # 初始化上传队列大小
        self.total = self.upload_list.qsize()
        self.working_directory = directory

    # 增加新的线程
    def add_thread(self):
        index = len(self.threads)
        thread = UploadingThread(number=index, direcotry= self.working_directory, q=self.upload_list, fail_record=self.fail_record)
        self.threads.append(thread)

    # 增加path所对应文件到队列
    def add_item(self, path):
        self.upload_list.put(path)
        self.total = self.upload_list.qsize()

    # 返回队列大小
    def get_total_number(self):
        return self.total

    def cleanall(self):
        self.upload_list = Queue()
        # print self.upload_list.qsize()

    def refresh_threads(self):
        index = len(self.threads)
        for i in range(index):
            self.add_thread()
