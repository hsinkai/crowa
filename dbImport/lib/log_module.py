# -*- coding: utf-8 -*-

import os
import time
import logging


class log_module:
    def __init__(self, file_path, flag='info'):

        self.file_path = file_path

        file_path = os.path.dirname(file_path)
        if not os.path.exists(file_path):
            os.makedirs(file_path)

        self.log_format = None
        self.logFormatter = logging.Formatter('%(asctime)s\n%(message)s\n')
        self.logger = logging.getLogger(file_path)
        self.logger.setLevel(getattr(logging, flag.upper()))

    def write(self, msg, flag='info'):

        if self.log_format != time.strftime('%Y%m%d'):

            if self.log_format is not None:
                self.logger.removeHandler(self.logHandler)
                self.logHandler.close()

            self.log_format = time.strftime('%Y%m%d')
            file_path = self.file_path + '.' + self.log_format

            self.logHandler = logging.FileHandler(file_path)
            self.logHandler.setFormatter(self.logFormatter)
            self.logger.addHandler(self.logHandler)

        getattr(self.logger, flag)(msg)
