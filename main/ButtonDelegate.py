# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from PyQt4 import QtGui, QtCore


# 每条传输进度上的两个按钮：失败信息 和 重试
class ButtonDelegate(QtGui.QItemDelegate):

    # 初始化
    def __init__(self):
        super(ButtonDelegate, self).__init__()

        # 用两个Dict分辨存储“失败信息”按钮 和 “重试”按钮
        self.fail_buttons = {}
        self.retry_buttons = {}
        # 用一个单独的list来储存该显示按钮delegate的行
        self.need_show = []

    # 渲染函数：控制按钮的显示
    def paint(self, painter, option, index):
        row = index.row()
        col = index.column()
        style = QtGui.QApplication.style()

        # 将第四列的表格转化为按钮
        if col == 4:

            # 构建一个新的失败信息按钮，并设置其初始设定
            button = QtGui.QStyleOptionButton()
            button.text = u"失败信息"
            button.rect = option.rect.adjusted(4, 4, -4, -4)

            # 当检测到当前行数还没有构建按钮的时候（如果需要激活按钮）
            if row in self.need_show:
                if row not in self.fail_buttons:
                    button.state |= style.State_Enabled
                    self.fail_buttons[row] = button
                else:
                    button.state |= self.fail_buttons[row].state
            style.drawControl(QtGui.QStyle.CE_PushButton, button, painter)

        elif col == 5:

            # 构建一个新的重试按钮，并设置其初始设定
            button = QtGui.QStyleOptionButton()
            button.text = u"重试"
            button.rect = option.rect.adjusted(4, 4, -4, -4)

            if row in self.need_show:
                # 当检测到当前行数还没有构建按钮的时候（如果需要激活按钮）
                if row not in self.retry_buttons:
                    button.state |= style.State_Enabled
                    self.retry_buttons[row] = button
                else:
                    button.state |= self.retry_buttons[row].state
            style.drawControl(QtGui.QStyle.CE_PushButton, button, painter)
        # 如不需要构建按钮，直接该画什么画什么
        else:
            QtGui.QItemDelegate.paint(self, painter, option, index)

    # 鼠标事件:
    def editorEvent(self, event, model, option, index):
        style = QtGui.QApplication.style()
        row = index.row()
        col = index.column()
        # 鼠标点击事件
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if option.rect.contains(event.x(), event.y()) and row in self.fail_buttons and col == 4:
                self.fail_buttons[row].state |= style.State_Sunken
            elif option.rect.contains(event.x(), event.y()) and row in self.retry_buttons and col == 5:
                self.retry_buttons[row].state |= style.State_Sunken
        # 鼠标松开事件
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            if option.rect.contains(event.x(), event.y()) and row in self.fail_buttons and col == 4:
                self.fail_buttons[row].state &= not style.State_Sunken
                # 发射失败信息显示信号
                self.emit(QtCore.SIGNAL("show_failure(int)"), row)
                self.fail_buttons[row].state |= style.State_Enabled
            elif option.rect.contains(event.x(), event.y()) and row in self.retry_buttons and col == 5:
                self.retry_buttons[row].state &= not style.State_Sunken
                # 发射重试信号
                self.emit(QtCore.SIGNAL("initiate_retry(int)"), row)
                self.retry_buttons[row].state |= style.State_Enabled
        return True

    # 更新需要显示的button
    def update_need_show(self, row):
        self.need_show.append(row)

    def clear_need_show(self):
        self.need_show = []

