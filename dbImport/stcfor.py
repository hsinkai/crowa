#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Filename: stcfor
Auchor: CJ Lin
"""

import os.path
import sys
import datetime
import glob
import math

import petl
import netCDF4
import numpy
from dateutil import parser, tz

import lib

head, tail = os.path.split(sys.argv[1])
inputstr = tail.split('_')[2]

if len(glob.glob(os.path.join(os.path.dirname(sys.argv[1]), 'ocm3_[thz]*' + inputstr + '_H*'))) == 12:
    timelen = 96
    home = os.path.expanduser("~")
    today = parser.parse(inputstr + '00+0000').astimezone(tz.tzlocal())

    dataset = {}
    for i in ('temp', 'hvel', 'zcor'):
        dataset[i] = netCDF4.MFDataset([os.path.join(head, 'ocm3_{0}_{1}_H{2}.nc'.format(i, inputstr, j))
                                        for j in ('-23_00', '01_24', '25_48', '49_72')])

    find = [-1, -5, -10]
    depth = petl.fromcolumns([find], ['depth'])

    points = petl.fromcsv(os.path.join(home, 'var', 'Points')).convert({'lat': float, 'lon': float, 'ncpos': int})
    pPoints = [int(x) for x in open(os.path.join(home, 'var', 'PengHu'))]
    nodelist = points.values('ncpos')

    zcorlist = dataset['zcor']['zcor'][:].take(nodelist, 2)
    templist = dataset['temp']['temp'][:].take(nodelist, 2)
    ulist = dataset['hvel']['u'][:].take(nodelist, 2)
    vlist = dataset['hvel']['v'][:].take(nodelist, 2)

    tempout = numpy.ndarray((timelen, 3, 189), numpy.float32)
    speedout = numpy.ndarray((timelen, 3, 189), numpy.float32)
    dirout = numpy.ndarray((timelen, 3, 189), numpy.float32)

    for x in range(timelen):
        for z in range(189):
            indices = zcorlist[x].take(z, 1).searchsorted(find)
            for j in range(3):
                k = indices[j] - 1 if indices[j] == 33 else min(indices[j] - 1, indices[j],
                                                                key=lambda y: abs(zcorlist[x][y][z] - find[j]))

                tempout[x][j][z] = dataset['temp']['temp'][x][k].take(pPoints).mean() if z == 186 else templist[x][k][z]
                speedout[x][j][z] = math.sqrt(ulist[x][k][z] ** 2 + vlist[x][k][z] ** 2)
                dirout[x][j][z] = math.atan2(ulist[x][k][z], vlist[x][k][z]) / 0.0174
                if dirout[x][j][z] < 0:
                    dirout[x][j][z] += 360

    table = petl.fromcolumns([dataset['temp']['time'][:]], ['time']
               ).convert('time', lambda x: today + datetime.timedelta(-2, int(x))
               ).crossjoin(depth
               ).crossjoin(points.cutout('ncpos')
               ).addcolumn('temp', tempout.flatten()
               ).addcolumn('speed', speedout.flatten()
               ).addcolumn('dir', dirout.flatten())

    for i in dataset:
        dataset[i].close()

    lib.db.DBWriter(table.convert('time', lambda x: x.replace(tzinfo=None)), 'STCFor', 'append')
    time = today + datetime.timedelta(hours=1)

    for name in ('Peng_Hu', 'Chang_Hua', 'Heng_chun', 'Che_Cheng', 'Liuqiu'):
        lib.stwarning.STWarning(name, time.replace(tzinfo=None), float(table.selecteq(('type', 'time'),
                                                                                      (name, time))[1][6]))
