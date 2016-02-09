# -*- coding: utf-8 -*-
__author__ = 'royyhma'
from PyQt4 import QtCore,QtGui
from main.TableLine import TableLineItem
from RecordHandler import RecordHandler


class MainTableModel(QtCore.QAbstractTableModel):
    def __init__(self, fail_record):
        super(MainTableModel, self).__init__()
        # 创建一个存储Tableline类的list（即显示的每一行）
        self.ListItem = []
        # 创建一个用文件名来查找函数的查询表
        self.lookup_table = {}
        # 创建一个写失败文件的记录器
        self.recorder = RecordHandler("fail")
        # 初始化，将file_list参数里的信息创建成tableline的列表
        self.file_list = []
        for path in self.file_list:
            item = TableLineItem(str(path))
            self.ListItem.append(item)
            self.lookup_table[str(path)] = item
        # 初始化传输失败列表
        self.fail_record = fail_record

    # 模型的行数为LIST的长度
    def rowCount(self, parent=None):
        return len(self.ListItem)

    # 模型的列数为7
    def columnCount(self, parent=None):
        return 7

    # 模型的数据设定
    def data(self, index, role):
        row = index.row()
        col = index.column()
        # 将列数1,3,7设置为空白
        if col == 0 or col == 6 or col == 2:
            if role == QtCore.Qt.DisplayRole:
                return QtCore.QVariant()
        # 将列数3设置为状态
        elif col == 3:
            if role == QtCore.Qt.DisplayRole:
                # 根据对应行数的状态来显示
                if self.ListItem[row].status == 0:
                    return QtCore.QVariant()
                elif self.ListItem[row].status == 1:
                    return "waiting..."
                elif self.ListItem[row].status == 2:
                    return "uploading..."
                elif self.ListItem[row].status == 3:
                    return "failed"
            # 设置颜色
            if role == QtCore.Qt.ForegroundRole:
                brush = QtGui.QBrush()
                if self.ListItem[row].status == 1:
                    brush.setColor(QtGui.QColor("black"))
                elif self.ListItem[row].status == 2:
                    brush.setColor(QtGui.QColor("blue"))
                else:
                    brush.setColor(QtGui.QColor("red"))
                return brush
        else:
            # 将2列设置为路径
            if role == QtCore.Qt.DisplayRole:
                value = self.ListItem[row].path
                return value

    # 加入一个心的Tableline物体
    def add_item(self, path="sample", status=0, parent=QtCore.QModelIndex()):
        position = len(self.ListItem)
        self.beginInsertRows(parent, position, position)
        item = TableLineItem(number=position, path=path, status=status)
        self.ListItem.append(item)
        self.lookup_table[item.path] = item
        self.endInsertRows()
        return True

    # 删除一个用路径path指定的Tableline物体
    def delete_item(self, path, parent=QtCore.QModelIndex()):
        item_to_delete = self.lookup_table[path]
        pos = self.ListItem.index(item_to_delete)
        del self.lookup_table[path]
        self.beginRemoveRows(parent, pos, pos)
        self.ListItem.remove(item_to_delete)
        self.endRemoveRows()
        return True

    # 将path指定的物品的状态设为waiting
    def update_status_to_waiting(self, path):
        item_to_change = self.lookup_table[path]
        item_to_change.status = 1
        self.refresh()

    # 将path指定的物品的状态设为uploading
    def update_status_to_uploading(self, path):
        item_to_change = self.lookup_table[path]
        item_to_change.status = 2
        self.refresh()

    # 将path指定的物品的状态设为完成即删除该物品
    def update_status_to_finished(self, path):
        try:
            self.delete_item(path)
        except KeyError:
            QtGui.QMessageBox.warning(self, u"警告", u"文件路径出现错误", QtGui.QMessageBox.Ok)
            self.emit(QtCore.SIGNAL("refresh_request"))
        self.refresh()

    # 将path指定的物品状态设置为failed, 并发出显示两个按钮的信号
    def update_status_to_failed(self, path):
        # 先从查询表里找到该物品
        item_to_change = self.lookup_table[path]
        item_to_change.status = 3
        row = item_to_change.line_number
        # 将该物品的行数发给delegate,因为delegate只认行数
        self.emit(QtCore.SIGNAL("show_buttons(int)"), row)
        self.refresh()

    # 弹出一个对话框显示失败信息
    def show_fail_msg(self, row):
        fail_dialog = QtGui.QDialog()
        item = self.ListItem[row]
        layout = QtGui.QVBoxLayout()
        if item.path in self.fail_record:
            message_label = QtGui.QLabel(self.fail_record[item.path])
            layout.addWidget(message_label)
        fail_dialog.setGeometry(0, 0, 200, 200)
        fail_dialog.setLayout(layout)
        fail_dialog.move(QtGui.QApplication.desktop().screenGeometry().center() - fail_dialog.rect().center())
        fail_dialog.setModal(True)
        fail_dialog.exec_()

    # 重试某一行的物品（在这里主要起文件名查询作用）
    def retry(self, row):
        item = self.ListItem[row]
        item_path = QtCore.QString(item.path)
        # 将文件名用信号的方式发射出去
        self.emit(QtCore.SIGNAL("retry(QString)"), item_path)

    # 更新模型
    def refresh(self):
        self.beginResetModel()
        self.endResetModel()

    def cleanall(self):
        self.ListItem = []
        self.lookup_table = {}
        self.refresh()

