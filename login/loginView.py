# -*- coding: utf-8 -*-
__author__ = 'royyhma'
import sys
from PyQt4 import QtCore, QtGui
from LoginWindow import Ui_Dialog
from main.uploader import Uploader


class LoginView(QtGui.QDialog):
    def __init__(self):
        super(LoginView, self).__init__()
        self. ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setFixedSize(self.width(),self.height())
        # 初始化用户信息
        self.app_id = ""
        self.secret_id = ""
        self.secret_key = ""
        self.bucket = ""
        self.working_directory = ""
        self.dir = QtCore.QDir()
        self.up_agent = Uploader()
        # 链接按钮信号
        self.ui.confirm_button.clicked.connect(self.login_check)
        self.ui.cancel_button.clicked.connect(self.close)
        self.ui.file_button.clicked.connect(self.open_file_nav)
        # 增加返回码exception
        self.execption_table = ['-1899', '-1893']
        self.ui.message_label.setStyleSheet("QLabel { color : red; }")
        # 初始化两个读写器
        self.config_ini = QtCore.QSettings("../main/pref.ini", QtCore.QSettings.IniFormat)
        self.info_ini = QtCore.QSettings("../main/userinfo.ini", QtCore.QSettings.IniFormat)

    def login_check(self):
        # 获取用户输入的值
        if self.empty_check():
            if self.directory_check() and self.internet_check():
                # 成功后将新的信息写入记录
                self.emit(QtCore.SIGNAL("login_succeed"))
                self.config_ini.setValue("/config/working_directory", self.working_directory)
                self.info_ini.setValue("/UserInfo/login", "True")
                self.info_ini.setValue("/UserInfo/appID", self.app_id)
                self.info_ini.setValue("/UserInfo/secretID", self.secret_id)
                self.info_ini.setValue("/UserInfo/secretKey", self.secret_key)
                self.info_ini.setValue("/UserInfo/bucket", self.bucket)
                self.close()
        else:
            pass

    def directory_check(self):
        # 检测路径是否合法
        if not self.dir.exists(self.working_directory):
            self.ui.message_label.setText(u"文件路径不合法")
        else:
            return True

    def internet_check(self):
        # 设置up_agent的值
        self.up_agent.set_app_id(str(self.app_id))
        self.up_agent.set_secret_id(str(self.secret_id))
        self.up_agent.set_secret_key(str(self.secret_key))
        self.up_agent.set_bucket(str(self.bucket))
        login_test_path = str(self.dir.current().absolutePath())
        login_test_path += "/login_test.jpg"
        print login_test_path
        obj = self.up_agent.upload_check(login_test_path, "login_test.jpg")
        # 返回值为200， 登录成功
        if obj['httpcode'] == 200:
            return True
        # 返回值为400， 查看特例
        elif obj['httpcode'] == 400:
            for instance in self.execption_table:
                if obj['code'] == instance:     # 特例满足，登录成功
                    return True
                else:   # 特例没有满足，登录失败
                    self.ui.message_label.setText(u"登录失败: "+obj['message'])
                    return False
        else:
            self.ui.message_label.setText(u"登录失败: "+obj['message'])
            return False

    def empty_check(self):
        # 获取用户输入值并注意检查，如果为空返回False
        self.app_id = self.ui.appID_line.text()
        self.secret_id = self.ui.secretID_line.text()
        self.secret_key = self.ui.secretKey_line.text()
        print self.secret_id
        self.bucket = self.ui.Bucket_Line.text()
        self.working_directory = self.ui.directory_line.text()
        # 每一行的空白与非法字符检测
        try:
                argument = str(self.app_id)
                if argument == "":
                    self.ui.message_label.setText(u"appID不能为空")
                    return False
        except UnicodeEncodeError:
                self.ui.message_label.setText(u"appID中含有非ASCII字符")
                return False

        try:
                argument = str(self.secret_id)
                if argument == "":
                    self.ui.message_label.setText(u"secretID不能为空")
                    return False
        except UnicodeEncodeError:
                self.ui.message_label.setText(u"secretID中含有非ASCII字符")
                return False

        try:
                argument = str(self.secret_key)
                if argument == "":
                    self.ui.message_label.setText(u"secretKey不能为空")
                    return False
        except UnicodeEncodeError:
                self.ui.message_label.setText(u"secretKey中含有非ASCII字符")
                return False

        try:
                argument = str(self.bucket)
                if argument == "":
                    self.ui.message_label.setText(u"bucket不能为空")
                    return False
        except UnicodeEncodeError:
                self.ui.message_label.setText(u"bucket中含有非ASCII字符")
                return False

        try:
                argument = str(self.working_directory)
                if argument == "":
                    self.ui.message_label.setText(u"文件路径不能为空")
                    return False
        except UnicodeEncodeError:
                self.ui.message_label.setText(u"文件路径中含有非ASCII字符")
                return False

        return True

    # 设置文件导航
    def open_file_nav(self):
        working_direcotry = QtGui.QFileDialog.getExistingDirectory(self, "Open Directory", "/home",QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks)
        self.ui.directory_line.setText(str(working_direcotry))


