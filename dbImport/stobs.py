#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Filename: stobs
Auchor: CJ Lin
"""

import os.path
import sys
import json

import petl
from dateutil import parser, tz

import lib

today = parser.parse(os.path.basename(sys.argv[1]).split('_')[0] + '000000+0000').astimezone(tz.tzlocal())
features = json.load(open(sys.argv[1]))['features']
data = petl.wrap((['name', 'oni', 'lon', 'lat', 'time', 'ws', 'sst'],))

for feature in features:
    properties = feature['properties']

    ws = petl.wrap(properties['ws'].items()).pushheader(('time', 'ws'))
    sst = petl.wrap(properties['sst'].items()).pushheader(('time', 'sst'))

    table = petl.wrap([['name', 'oni', 'lon', 'lat'], [properties['name'], properties['oni']] + feature['geometry']['coordinates']]
               ).annex(ws.outerjoin(sst)
               ).filldown('name', 'oni', 'lon', 'lat'
               ).convert('time', lambda x: parser.parse(x + '+0000').astimezone(tz.tzlocal()))

    select = table.selecteq('time', today)
    if len(select) > 1:
        lib.stwarning.STWarningWriter(properties['name'], today.replace(tzinfo=None), float(select[1][6]))
    data = data.stack(table)

lib.db.DBWriter(data.convert('time', lambda x: x.replace(tzinfo=None)), 'STObs', 'append')
