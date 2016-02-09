# -*- coding: utf-8 -*-
import time
import tencentyun


class Uploader:
    def __init__(self, app_id='', secret_id='', secret_key='', bucket=''):
        # self.app_id = '10000037'
        # self.secret_id = 'AKIDpoKBfMK7aYcYNlqxnEtYA1ajAqji2P7T'
        # self.secret_key = 'P4FewbltIpGeAbwgdrG6eghMUVlpmjIe'
        # self.bucket = 'test0706'
        self.app_id = app_id
        self.secret_id = secret_id
        self.secret_key = secret_key
        self.bucket = bucket
        self.file_id = 'sample'+str(int(time.time()))

    def upload(self, absolute_path, relatetive_path):
        # 图片上传
        self.file_id = relatetive_path
        image = tencentyun.ImageV2(self.app_id, self.secret_id, self.secret_key)
        obj = image.upload(absolute_path, self.bucket, self.file_id)
        print obj

        print image.delete(self.bucket, self.file_id)
        return obj

    def upload_check(self, absolute_path, relatetive_path):
        # 图片上传
        self.file_id = relatetive_path
        image = tencentyun.ImageV2(self.app_id, self.secret_id, self.secret_key)
        obj = image.upload(absolute_path, self.bucket, self.file_id)
        print obj

        print image.delete(self.bucket, self.file_id)
        return obj

    def set_app_id(self, app_id):
        self.app_id = app_id

    def set_secret_id(self, secret_id):
        self.secret_id = secret_id

    def set_secret_key(self, secret_key):
        self.secret_key = secret_key

    def set_bucket(self, bucket):
        self.bucket = bucket


