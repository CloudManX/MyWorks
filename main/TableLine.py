# -*- coding: utf-8 -*-
__author__ = 'royyhma'


# 界面上的行数物品
class TableLineItem:
    def __init__(self, number, path="sample", status=0):
        # 文件路径/文件名
        self.path = path
        # 该文件的状态
        self.status = status
        # 该文件的行数
        self.line_number = number

    def get_path(self):
        return self.path

    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status
