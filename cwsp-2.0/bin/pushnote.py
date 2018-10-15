#!/home/crsadm/.conda/envs/crs-py27/bin/python
# coding=utf-8

import getopt
import os
import sys
import time
import logging


if __name__ == '__main__':
    usage = u"""
Usage:
    ./pushnote.py [options] arguments
options:
    -f: 指定設定檔
    -p, --push_url: 指定推播服務的URL
    -u, --update_url: 指定 Web API Service URL
argument:
    指定資料來源(檔案路徑 or 資料表 or 資料名稱)

使用範例:
    export CWSP_CONFIG_PATH=~/cfg/cwsp.yaml
    ./pushnote.py --push_url={PUSH_MESSAGES_SERVICE_URL} --update_url={WEB_API_URLS} AquaCulture

範例說明：
    截取資料表`CRSdb`.`AquaCulture`的內容以決策是否通知
    推播服務'{PUSH_MESSAGES_SERVICE_URL}';
    推播歷史記錄於`CRSdb`.`his_notification`。
    再更新 Web API Service cacheing。
""".encode(sys.getfilesystemencoding())

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hf:p:u:', ['help', 'push_url=', 'update_urls=', ])
    except Exception as e:
        raise SystemExit(str(e) + "\nTry './pushnote.py --help'")

    # initial application context(configuration)
    from cwsp.conf import Context, CONFIG_ENVAR_PATH
    Context.init_config(opts)
    for opt, arg in opts:
        if ('-p' == opt) or ('--push_url' == opt):
            Context.config['PUSH_MESSAGES_SERVICE_URL'] = arg
        if ('-u' == opt) or ('--update_urls' == opt):
            Context.config['REST_API_CACHE_SERVICE_URLS'] = arg.split(';')

    # handle help
    for opt, _ in opts:
        if opt in ('-h', '--help'):
            msg = usage.format(
                PUSH_MESSAGES_SERVICE_URL=Context.config['PUSH_MESSAGES_SERVICE_URL'],
                WEB_API_URLS=';'.join(Context.config['REST_API_CACHE_SERVICE_URLS']),
            )
            print msg
            raise SystemExit

    assert (os.environ.get(CONFIG_ENVAR_PATH) is not None), u'找不到定設定檔'.encode(sys.getfilesystemencoding())
    assert (len(args) > 0), u'未指定資料來源'.encode(sys.getfilesystemencoding())

    # initial application logger
    log_file_path = os.path.join(Context.config['LOG_DIR'], 'CWSP_pushnote.%s' % time.strftime('%Y%m%d'))
    Context.init_logger(filename=log_file_path, level=Context.config['LOG_LEVEL'])
    Context.logger.addHandler(logging.StreamHandler(sys.stdout))

    # start application
    Context.logger.info("Command: " + ' '.join(sys.argv))
    from cwsp.pushnote.dispatchers import Dispatcher
    for data_source in args:
        Dispatcher(data_source).process()

