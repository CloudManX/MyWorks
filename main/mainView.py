# -*- coding: utf-8 -*-
__author__ = 'royyhma'
import sys
from PyQt4 import QtGui, QtCore
from main.MainWindow import Ui_MainWindow
from main.DynamicComponent import DynamicComponent
from pref.prefView import PrefView
from login.loginView import LoginView


class MainView(QtGui.QMainWindow):
    def __init__(self):
        super(MainView, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # 静态外观设定
        self.setFixedSize(self.width(),self.height())
        self.ui.tableView.setShowGrid(False)
        self.ui.tableView.verticalHeader().setVisible(False)
        horizontal_header = self.ui.tableView.horizontalHeader()
        for item in range(horizontal_header.count()-1):
            horizontal_header.setSectionResizeMode(item, QtGui.QHeaderView.Stretch)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setTextVisible(False)
        self.ui.retryAllButton.setDisabled(True)

        # 动态模块
        self.dynam = DynamicComponent()
        if self.dynam.is_auto_sync == 1:
            self.ui.controlButton.setDisabled(True)
        # 设置模型
        self.ui.tableView.setModel(self.dynam.controller.model)
        # 设置代表
        self.ui.tableView.setItemDelegate(self.dynam.delegate)
        # 静态按钮连接：
        # 开启选项界面信号
        self.ui.prefButton.clicked.connect(self.go_to_pref)
        # 手动开始任务信号
        self.ui.controlButton.clicked.connect(self.mission_control)
        # 刷新
        self.ui.refresh_button.clicked.connect(self.restart)
        # 将线程连接到进度条
        for thread in self.dynam.controller.uploader.threads:
            # 失败状态时，激活重试与失败信息的按钮
            self.connect(thread, QtCore.SIGNAL("progress_need_to_change(int)"), self.update_progress)
        # 开始重新传输全部失败文件
        self.ui.retryAllButton.clicked.connect(self.dynam.controller.retry_all)
        self.ui.retryAllButton.clicked.connect(self.mission_control)
        self.connect(self.dynam.controller.model, QtCore.SIGNAL("refresh_requsted"), self.restart)
        # 读写器
        self.info_ini = QtCore.QSettings("../main/userinfo.ini", QtCore.QSettings.IniFormat)

    # 主任务控制函数
    def mission_control(self):
        # 如果当前任务并未执行，则开始任务
        if self.dynam.running_status == 0:
            self.dynam.mission_start()
            if self.dynam.controller.uploader.upload_list.qsize() > 0:
                self.dynam.running_status = 1
                self.ui.retryAllButton.setDisabled(True)
                self.ui.refresh_button.setDisabled(True)
                self.ui.controlButton.setText(u"暂停")
        elif self.dynam.running_status == 1:
            self.dynam.mission_stop()
            self.dynam.running_status = 2
            self.ui.controlButton.setText(u"继续")
        elif self.dynam.running_status == 2:
            self.dynam.mission_resume()
            self.dynam.running_status = 1
            self.ui.retryAllButton.setDisabled(True)
            self.ui.refresh_button.setDisabled(True)
            self.ui.controlButton.setText(u"暂停")

    # 更新进度条
    def update_progress(self, number):
        # 计算进度条值
        total = self.dynam.controller.uploader.total
        value = (total - number)*100/total
        # 设置值
        self.ui.progressBar.setValue(value)
        if value == 100:
            self.ui.controlButton.setText(u"开始")
            self.ui.retryAllButton.setEnabled(True)
            self.ui.refresh_button.setEnabled(True)
            self.dynam.running_status = 0

    # 开启控制面板
    def go_to_pref(self):
        # 控制面板居中
        # 控制面板
        panel = PrefView(self.dynam.running_status)
        # 当工作路径变化时，链接重启信号
        self.connect(panel, QtCore.SIGNAL("restart_requested"), self.restart)
        # 链接更新并发数信号
        self.connect(panel, QtCore.SIGNAL("thread_update_requested(int)"), self.dynam.update_thread_number)
        # 链接更新同步设定信号
        self.connect(panel, QtCore.SIGNAL("sync_status_update_requested(int)"), self.update_sync_status)
        # 链接切换用户信号
        self.connect(panel, QtCore.SIGNAL("switch_requested"), self.switch)
        panel.move(QtGui.QApplication.desktop().screenGeometry().center() - panel.rect().center())
        panel.setModal(True)
        panel.exec_()

    # 重新来过
    def restart(self):
        print "restart"
        # 停止现在执行的工作
        if self.dynam.running_status == 1:
            self.dynam.mission_stop()
        self.dynam = DynamicComponent()
        self.ui.tableView.setModel(self.dynam.controller.model)
        self.ui.tableView.setItemDelegate(self.dynam.delegate)
        for thread in self.dynam.controller.uploader.threads:
            # 失败状态时，激活重试与失败信息的按钮
            self.connect(thread, QtCore.SIGNAL("progress_need_to_change(int)"), self.update_progress)
        # 开始重新传输全部失败文件
        self.ui.retryAllButton.clicked.connect(self.dynam.controller.retry_all)
        self.ui.retryAllButton.clicked.connect(self.dynam.mission_resume)
        self.connect(self.dynam.controller.model, QtCore.SIGNAL("refresh_requsted"), self.restart)
        self.ui.controlButton.setText(u"开始")
        self.ui.progressBar.setValue(0)

    # 更新同步状态
    def update_sync_status(self, status):
        if status == 1:
            self.dynam.is_auto_sync = 1
            self.ui.controlButton.setDisabled(True)
        elif status == 0:
            self.dynam.is_auto_sync = 0
            self.ui.controlButton.setEnabled(True)
        else:
            print "Status Error Occured!"

    def login(self):
        is_logined = str(self.info_ini.value("UserInfo/login").toString())
        if is_logined == "True":
            self.show()
        else:
            login_dialog = LoginView()
            self.connect(login_dialog, QtCore.SIGNAL("login_succeed"), self.login_jump)
            login_dialog.exec_()

    def login_jump(self):
            print "jumpted"
            self.show()

    def switch(self):
        #   停止现有进程
        if self.dynam.running_status == 1:
            self.dynam.mission_stop()
        self.info_ini.setValue("/UserInfo/login", "False")
        # 重启自己
        self.close()
        self.login()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    main = MainView()
    main.login()
    sys.exit(app.exec_())
