#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Filename: stationdaylight
Auchor: CJ Lin
"""

import sys
import re
import datetime

import petl


def parsetime(obsTime):
    year, month, day, hour, minute = re.search('(\d{4})/(\d{2})/(\d{2}) (\d{2}):(\d{2})', obsTime).groups()
    return datetime.datetime(int(year), int(month), int(day)) + datetime.timedelta(minutes=int(minute), hours=int(hour))

petl.fromcsv(sys.argv[1]).convert('`obsTime`', parsetime).tocsv(sys.argv[1]+'.bak')
