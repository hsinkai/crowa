#!/home/crsadm/.conda/envs/crs-py27/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import datetime
import logging

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, basedir)

from cwsp.conf import CONFIG_ENVAR_PATH, Context


if __name__ == "__main__":
    ###############################################
    # python bin\rc_updater.py -src_db_label 61.56.13.154/NAGRdb -dst_db_label test-localhost short-term
    ###############################################

    description = u"""
     jsonbuilder.py 截取資料，產制json，然後推到前台 Web API。
     使用範例:
         export CWSP_CONFIG_PATH=~/cfg/cwsp-2.0.yaml
         ./jsonbuilder.py [options] positions
    """

    # parse commandline for apps
    arg_parser = argparse.ArgumentParser(description)
    json_dump_dir = os.path.join(basedir, 'jsonfile')
    post_url = 'http://61.60.103.185:33333/api/v2.0/cwsp/update'
    arg_parser.add_argument('target', help=u"指定資料源名稱或 'all-table'。")
    arg_parser.add_argument('-f', default=os.environ.get(CONFIG_ENVAR_PATH), help=u"指定設定檔，預設取環境變數 $%s。" % CONFIG_ENVAR_PATH)
    arg_parser.add_argument('-product', default=None, help=u"指定要產制的產品名稱。")
    args = arg_parser.parse_args()

    # does configuration for this apps
    Context.init_config(config_path=args.f)
    Context.init_logger(filename='%s.%s' % ('jsonbuilder', datetime.datetime.now().strftime('%Y%m%d')))
    Context.logger.addHandler(logging.StreamHandler())
    Context.logger.info('Command: %s' % sys.argv)
    Context.logger.debug("Using config file: '%s'" % Context.get_attrib('config_path'))

    # start apps
    Context.logger.info("Command: " + ' '.join(sys.argv))

    from cwsp.jsonbuilder.dispatchers import (
        DataTableDispatcher,
        ArchiveDispatcher,
        FileDispatcher,
        DirDispatcher,
        ProductDispatcher,
    )

    if args.product:
        ProductDispatcher(args.target, args.product).process()
    elif (args.target.endswith('.zip') or args.target.endswith('.tar')) and os.path.isfile(args.target):
        ArchiveDispatcher(args.target).process()
    elif os.path.isdir(args.target):
        DirDispatcher(args.target).process()
    elif os.path.isfile(args.target):
        FileDispatcher(args.target).process()
    else:
        DataTableDispatcher(args.target).process()
