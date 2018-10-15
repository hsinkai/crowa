#!/home/crsadm/.conda/envs/crs-py27/bin/python
# -*- coding: utf-8 -*-

import os
import zipfile
import argparse
import shutil
import warnings
from threading import Lock


def clean_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print 'remove file:', file_path
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print 'remove folder:', file_path
            else:
                raise RuntimeError("Unknow file type with path '%s'" % file_path)
        except Exception as e:
            warnings.warn(str(e))


def unzip(archive, data_pool, clean_data_pool):
    lock = Lock()
    with lock:
        if clean_data_pool and os.path.exists(args.target):
            clean_folder(args.target)
        if not os.path.exists(data_pool):
            os.makedirs(data_pool)
        _zip = zipfile.ZipFile(archive)
        try:
            _zip.extractall(data_pool)
        finally:
            _zip.close()
    print 'unzip %s --> %s' % (archive, data_pool)


if __name__ == '__main__':
    # parse commandline
    target_folder = './'
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('archive', help=u"zip file 路徑.")
    arg_parser.add_argument('-target', default=target_folder, help=u"目標目錄，解壓縮到該目錄， 預設：%s" % target_folder)
    arg_parser.add_argument('-clean_target', default='flase', help=u"是否清空目標目錄，合法值為 {'true' | 'flase' }，預設 true")
    args = arg_parser.parse_args()
    args.clean_target = True if (args.clean_target.upper() == 'TRUE') else False

    unzip(args.archive, args.target, args.clean_target)
