#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import datetime

import petl

import db
import log_module

home = os.path.expanduser("~")
log = log_module.log_module(os.path.join(home, 'log', 'dbImport'))
dbCfg = os.path.join(home, 'cfg', 'db.xml')


def STWarning(name, today, temp):
    days = []

    with db.Connector('crs') as cursor:
        cursor.execute('SET SQL_MODE=ANSI_QUOTES')

        for j in xrange(3):
            days.append(petl.fromdb(cursor, '''select `time`, temp from STCFor
                                    where temp = (select min(temp) from STCFor
                                        where '{first}' <= `time`
                                        and `time` < '{second}'
                                        and `type` = '{name}'
                                        and depth = -1)
                                    and '{first}' <= `time`
                                    and `time` < '{second}'
                                    and `type` = '{name}'
                                    and depth = -1'''.format(first=today + datetime.timedelta(j),
                                                    second=today + datetime.timedelta(j+1), name=name))[1])

        cursor.execute('''SELECT MAX(fhs)
                        FROM Wave
                        WHERE `type` = '{0}'
                        AND '{time}' >= `time`
                        AND ('{time}' < `time` + INTERVAL 1 DAY)'''.format(name, time=today))
        maxfhs = cursor.fetchall()[0][0]

    maxDay = max(days, key=lambda x: x[1])
    minDay = min(days, key=lambda x: x[1])
    location = '澎湖' if name == 'Peng_Hu' else '彰化' if name == 'Chang_Hua' else '恆春' if name == 'Heng_chun' else '車城' if name == 'Che_Cheng' else '琉球'

    if maxDay[1] - minDay[1] < 0.1:
        token = '呈現持平'

    elif days[0][1] >= days[1][1] >= days[2][1]:
        token = '有降低趨勢'

    elif days[0][1] <= days[1][1] <= days[2][1]:
        token = '有上升趨勢'

    else:
        token = '呈現震盪，震盪幅度{0}度'.format(round(maxDay[1]-minDay[1], 1))

    token2 = '，最低溫出現在{0}月{1}日{2}時，與{3}月{4}日早上{5}時相較{6}{7}度'.format(
        minDay[0].month, minDay[0].day, minDay[0].hour, today.month, today.day, today.hour,
        '高' if temp < minDay[1] else '低', round(abs(temp-minDay[1]), 1)) if round(abs(temp-minDay[1]), 1) != 0 else ''

    warning = '{0}月{1}日早上{2}時{loc}海溫{3}度，海溫預報顯示{loc}最低海溫{4}{5}。'.format(
        today.month, today.day, today.hour, round(temp, 1), token, token2, loc=location).decode('utf8')

    db.DBWriter(petl.wrap([['name', 'time', 'warning', 'max_fhs'], [name, today, warning, maxfhs]]),
                'STWarning', 'append')
