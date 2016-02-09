# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QMessageBox
from pref.PrefWindow import Ui_Dialog


class PrefView(QtGui.QDialog):
    def __init__(self, running_status):
        super(PrefView, self).__init__()
        self.running_status = running_status
        # 界面设定
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(),self.height())
        # 读ini文件中现在的工作路径
        self.config_ini = QtCore.QSettings("pref.ini", QtCore.QSettings.IniFormat)
        self.working_directory = self.config_ini.value("/config/working_directory").toString()
        self.ui.path_line.setText(self.working_directory)
        # 链接按钮信号
        self.ui.confirm_button.clicked.connect(self.update_config)
        self.ui.switch_button.clicked.connect(self.switch_user)
        self.ui.cancel_button.clicked.connect(self.close)
        self.ui.file_button.clicked.connect(self.open_file_nav)
        # 读ini文件中现在的并发数
        self.thread_number = int(self.config_ini.value("/config/thread_number").toString())
        self.ui.con_line.setText(str(self.thread_number))
        # 读ini文件中的同步选项
        self.is_auto_sync = int(self.config_ini.value("/config/is_auto_sync").toString())
        if self.is_auto_sync:
            self.ui.checkBox.setCheckState(QtCore.Qt.Checked)
        self.check_pass = True
        self.is_working_directory_changed = False
        self.is_thread_number_changed = False
        self.is_auto_sync_changed = False

    # 更新当前处理的路径
    def update_config(self):
        # 检查三个用户选项
        self.close_check(self.check_working_directory())
        self.close_check(self.check_thread_number())
        self.close_check(self.check_auto_sync())
        # 若全部通过，开始更新列表
        if self.check_pass:
            self.config_ini.setValue("/config/working_directory", self.working_directory)
            self.config_ini.setValue("/config/thread_number", str(self.thread_number))
            self.config_ini.setValue("/config/is_auto_sync", str(self.is_auto_sync))
            self.close()
        else:
            self.check_pass = True
            return
        if self.is_working_directory_changed:
            if self.running_status > 0:
                message_box = QtGui.QMessageBox.question(self, u"警告", u"检测到同步正在进行，是否种终止进程以实现目录变更",
                                                         QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if message_box == QtGui.QMessageBox.Yes:
                    # 发射中止并重启信号
                    self.emit(QtCore.SIGNAL("restart_requested"))
                elif message_box == QtGui.QMessageBox.No:
                    pass
            else:
                self.emit(QtCore.SIGNAL("restart_requested"))
        else:
            if self.is_thread_number_changed:
                    self.emit(QtCore.SIGNAL("thread_update_requested(int)"), self.thread_number)
            if self.is_auto_sync_changed:
                    self.emit(QtCore.SIGNAL("sync_status_update_requested(int)"), self.is_auto_sync)

    # 检查文件路径，当没有问题时返回True
    def check_working_directory(self):
        user_input_directory = self.ui.path_line.text()
        directory = QtCore.QDir()
        # 如果文件路径为空或并未作出更改
        if user_input_directory == "" or user_input_directory == self.working_directory:
            return True
        # 检查文件的合法性
        elif not directory.exists(user_input_directory):
            QMessageBox.warning(self, u"警告", u"路径不合法", QtGui.QMessageBox.Ok)
            return False
        # 如果以上情况都不符合，证明用户希望更改目录
        else:
            self.working_directory = user_input_directory
            self.is_working_directory_changed = True
            return True

    # 检查并发数
    def check_thread_number(self):
        # 用户输入值是否是数字
        try:
            thread_number = int(self.ui.con_line.text())
            # 检测用户输入数字是否在限制之内（1-20）
            if thread_number > 20 or thread_number < 1:
                QMessageBox.warning(self, u"警告", u"并发数必须在1至20之间", QtGui.QMessageBox.Ok)
                return False
            elif thread_number == self.thread_number:
                self.is_thread_number_changed = False
                return True
            else:
                # 若条件满足，发射更新并发数信号
                self.thread_number = thread_number
                self.is_thread_number_changed = True
                return True
        # 用户输入造成valueError
        except ValueError:
            text = self.ui.con_line.text()
            # 检测用户是不是没有使用操作
            if text == "":
                return True
            else:
                QMessageBox.warning(self, u"警告", u"请在并发数输入数字", QtGui.QMessageBox.Ok)
                return False

    # 检查自动同步选项是否有改动
    def check_auto_sync(self):
        # 如果用户希望开启自动同步，将state升级为1
        if self.ui.checkBox.isChecked():
            state = 1
        else:
            state = 0             # 反之，将state设置为0
        if not state == self.is_auto_sync:  # 检测同步选项是否改变
            self.is_auto_sync = state
            self.is_auto_sync_changed = True
        else:
            self.is_auto_sync_changed = False
        return True     # 用户不可能在此项目有不合法输入

    def close_check(self, check):
        if self.check_pass and not check:
            self.check_pass = False

    # 切换用户检查
    def switch_user(self):
        # 若有任务正在进行
        if self.running_status > 0:
                message_box = QtGui.QMessageBox.question(self, u"警告", u"检测到同步正在进行，是否种终止进程以切换用户",
                                                         QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if message_box == QtGui.QMessageBox.Yes:
                    # 发射中止并重启信号
                    self.emit(QtCore.SIGNAL("switch_requested"))
                    self.close()
                elif message_box == QtGui.QMessageBox.No:
                    pass
        else:
            # 若检查通过，关闭控制面板并发射信号
            self.close()
            self.emit(QtCore.SIGNAL("switch_requested"))

    # 设置文件导航
    def open_file_nav(self):
        working_direcotry = QtGui.QFileDialog.getExistingDirectory(self, "Open Directory", "/home",QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks)
        self.ui.path_line.setText(str(working_direcotry))
