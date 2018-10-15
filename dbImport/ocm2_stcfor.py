#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Filename: stcfor
Auchor: CJ Lin
"""

import sys

import petl

petl.fromcsv(sys.argv[1], delimiter=' ', skipinitialspace=True
   ).convert('YYYYMMDDHH', petl.datetimeparser('%Y%m%d%H')
   ).setheader(('time', -1, -5, -10)
   ).melt(('time')
   ).rename({'variable': 'depth', 'value': 'temp'}
   ).tocsv('ocm2_stcfor.csv')
