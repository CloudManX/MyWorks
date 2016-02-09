# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from PyQt4 import QtCore
from main.FileDetector import FileMonitor
from main.FileHandler import FileHandler
from main.MainTableModel import MainTableModel
from main.UploadController import UploadController


class MainController(QtCore.QObject):
    def __init__(self):
        super(MainController, self).__init__()
        self.config_ini = QtCore.QSettings("pref.ini", QtCore.QSettings.IniFormat)
        # 读ini文件中现在的并发数
        self.thread_number = int(self.config_ini.value("/config/thread_number").toString())
        # 文件检测器
        self.monitor = FileMonitor()
        # 记录现在工作路径
        self.working_direcotry = self.monitor.directory
        # 获取现有文件列表
        self.curr_file_list = self.monitor.get_all_path()
        # 监听是否目录被更改
        self.monitor.watcher.directoryChanged.connect(self.directory_handling)
        # 读取之前传输记录
        self.success_handler = FileHandler("success")
        self.success_record = self.success_handler.readFile()
        # 失败记录初始化
        self.fail_record = {}
        # 用文件初始化模型
        self.model = MainTableModel(fail_record=self.fail_record)
        # 初始化上传队列
        self.uploader = UploadController(fail_record=self.fail_record, directory=self.working_direcotry)
        # 依据并发数加入线程
        for i in range(self.thread_number):
            self.uploader.add_thread()
        # 第一次判定
        self.first_time = True
        self.should_sync = False

    # 将文件加入到list
    def directory_handling(self):
        # 读取成功记录
        self.success_record = self.success_handler.readFile()
        # 得到新的文件列表
        new_file_list = self.update_file_list()
        # 处理用户在当前目录下更改文件名的行为
        for my_file in self.model.ListItem:
            file_dir = QtCore.QDir()
            if not file_dir.exists(my_file.path):
                # print my_file
                self.deleting(my_file.path)
        # 更新View里的列表
        for my_file in new_file_list:
            # 未曾传输的文件
            if my_file not in self.success_record:
                # 且这是第一次操作或该文件是新加入到当前路径中来的
                if my_file not in self.curr_file_list or self.first_time:
                    self.adding(my_file)
                    self.should_sync = True
                    # print unicode(my_file, encoding="UTF-8")
        if self.should_sync:
                    # 发射自动同步信号
                    self.emit(QtCore.SIGNAL("auto_sync_should_start"))
        # 更新当前列表（即文件记录）
        self.curr_file_list = new_file_list

    # 增加文件
    def adding(self, path):
        self.model.add_item(path)

    def deleting(self, path):
        self.model.update_status_to_finished(path)

    # 得到最新列表
    def update_file_list(self):
        return self.monitor.get_all_path()

    # 将某个特定Path的文件的状态设置为uploading
    def update_status_1(self):
        # print path
        for item in self.model.ListItem:
            if item.status == 0:
                path = item.path
                self.uploader.add_item(path)
                self.model.update_status_to_waiting(path)

    def update_status_2(self, path):
        # print path
        self.model.update_status_to_uploading(path)

    # 成功完成此文件后，写入成功列表并从传输列表中删除
    def update_status_x(self, path):
        # print path
        self.model.update_status_to_finished(path)
        self.success_handler.writeFile(path)

    # 将某个特定Path的文件的状态设置为failed
    def update_status_3(self, path):
        # print path
        self.model.update_status_to_failed(path)

    # 重试某个特定path的失败文件
    def retry(self, path):
        # 删除文件并重新加入列表
        self.model.update_status_to_finished(path)
        self.adding(path)

    # 重试全部失败文件
    def retry_all(self):
        for item in self.model.ListItem:
            if item.status == 3:
                item.status = 1
                self.uploader.upload_list.put(item.path)

    def clear_fail_record(self):
        self.fail_record = {}

