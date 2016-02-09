# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from PyQt4 import QtCore
from main.ButtonDelegate import ButtonDelegate
from main.MainController import MainController


class DynamicComponent(QtCore.QObject):
    def __init__(self):
        super(DynamicComponent, self).__init__()
        # 进程控制
        self.running_status = 0  # 0：停止， 1：进行， 2：暂停
        self.config_ini = QtCore.QSettings("pref.ini", QtCore.QSettings.IniFormat)
        self.is_auto_sync = int(self.config_ini.value("/config/is_auto_sync").toString())
        # self.finished_thread = 0    # 线程的完成数
        # 构建辅助控制器
        self.controller = MainController()
        # 搭建按钮委托（retry 和 fail_info)
        self.delegate = ButtonDelegate()
        # 简化线程集合threads调用
        self.threads_overview = self.controller.uploader.threads
        # 多线程动作连接
        self.thread_signal_handling()
        # 动态（列表中）按钮动作连接
        # 显示该单位失败信息
        self.connect(self.delegate, QtCore.SIGNAL("show_failure(int)"), self.controller.model.show_fail_msg)
        # 激活两个按钮
        self.connect(self.controller.model, QtCore.SIGNAL("show_buttons(int)"), self.delegate.update_need_show)
        # 按钮的代理向模型发出开始重试请求，若成功模型将发射一个带有文件路径的retry信号
        self.connect(self.delegate, QtCore.SIGNAL("initiate_retry(int)"), self.controller.model.retry)
        # 将模型发出的retry信号发布给主控制器和主界面
        self.connect(self.controller.model, QtCore.SIGNAL("retry(QString)"), self.controller.retry)
        self.connect(self.controller.model, QtCore.SIGNAL("retry(QString)"), self.mission_start)
        # 链接自动传输信号
        self.connect(self.controller, QtCore.SIGNAL("auto_sync_should_start"), self.auto_sync_control)
        # 初始文件检测
        self.controller.directory_handling()
        self.controller.first_time = False

    # 设置线程信号
    def thread_signal_handling(self):
        for thread in self.threads_overview:
            # 升级到上传状态，即从传输列表中更新为uploading
            self.connect(thread, QtCore.SIGNAL("started(QString)"), self.controller.update_status_2)
            # 升级到成功状态，即从传输列表中怒删该单位
            self.connect(thread, QtCore.SIGNAL("uploaded(QString)"), self.controller.update_status_x)
            # 升级到失败状态
            self.connect(thread, QtCore.SIGNAL("failed(QString)"), self.controller.update_status_3)
            # 每当一个线程完成自己的任务后，呼叫线程统计finish_count函数
            if self.running_status == 1:
                    thread.start()

    # 开始任务
    def mission_start(self):
        self.controller.update_status_1()
        print "uploading size is %d" % self.controller.uploader.upload_list.qsize()
        for thread in self.threads_overview:
            thread.is_stop = False
            thread.start()

    # 中断任务
    def mission_stop(self):
        for thread in self.threads_overview:
            thread.is_stop = True
        # 更新进程控制函数

    # 继续任务
    def mission_resume(self):
        for thread in self.threads_overview:
            thread.is_stop = False
            thread.start()
        # 更新进程控制函数

    # 更新并发数
    def update_thread_number(self, number):
        self.controller.concurrent_number = number
        # 如果新的并发数小于原来的线程数
        index = len(self.threads_overview)
        difference = abs(index - number)
        if index > number:
            for i in range(difference):
                # 从list中弹出最后一个线程
                thread = self.threads_overview.pop()
                # 在这线程完成其任务后停止它
                thread.is_stop = True
        elif index < number:
            for i in range(difference):
                # 往list中加一个线程
                self.controller.uploader.add_thread()
            self.thread_signal_handling()

    def auto_sync_control(self):
        print "hello"
        if self.is_auto_sync == 1:
            self.mission_start()
            self.controller.should_sync = False
            self.running_status = 1
        elif self.is_auto_sync == 0:
            pass
