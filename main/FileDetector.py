# -*- coding: utf-8 -*-
__author__ = 'Ma'
from PyQt4 import QtCore


class FileMonitor:
    def __init__(self):
        self.config_ini = QtCore.QSettings("pref.ini", QtCore.QSettings.IniFormat)
        # 新建一个文件监控
        self.watcher = QtCore.QFileSystemWatcher()
        self.directory = self.config_ini.value("/config/working_directory").toString()
        print "working directory now is" + self.directory
        self.dir = QtCore.QDir(self.directory)
        self.watch_record = []
        self.watcher.addPath(self.directory)
        self.watch_record.append(self.directory)
        self.dirs = []
        self.paths = []
        self.counter = 0

    # 以QString的形式返回所有在列表的文件路径
    def get_all_path(self):
        self.dir.setPath(self.directory)
        self.dirs = []
        self.paths = []
        paths = self.get_all_path_helper(self.dirs, self.paths)
        # print paths
        return paths

    # 迭代算法将路径下的文件拆包
    def get_all_path_helper(self, dirs, paths):
        # 获取全部文件并加入到列表中
        self.dir.refresh()
        file_info = self.dir.entryInfoList(QtCore.QDir.Files)
        for info in file_info:
            paths.append(info.absoluteFilePath())
        # 获取全部路径，并加入到dirs列表中
        dir_info = self.dir.entryInfoList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
        for info in dir_info:
            if not info == self.dir.currentPath():
                dirs.append(info.absoluteFilePath())
        # 如果当前路径中没有其他子路径
        if len(dirs) == 0:
            return paths
        else:
            # 获取文件中最后一个路径
            new_directory = dirs.pop()
            # 更新现在所操作的路径
            self.dir.setPath(new_directory)
            # 检测新的文件路径是否已被监听
            if new_directory not in self.watch_record:
                self.watcher.addPath(new_directory)
                self.watch_record.append(new_directory)
            # 获取该路径中的全部文件
            return self.get_all_path_helper(dirs, paths)

    # 更新现在的操作路径
    def update_directory(self, directory):
        # 检测用户有没有重复输入原来的路径
        if not directory == self.dir.absolutePath():
            self.dir.setPath(directory)
            self.directory = directory
            # print self.dir.absolutePath()
            self.watcher.addPath(directory)
