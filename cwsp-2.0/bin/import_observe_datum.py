#!/home/crsadm/.conda/envs/crs-py27/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import traceback

import petl

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


from dbman import RWProxy


def extract():
    sql = """SELECT main.* FROM(
                SELECT `StationID`, MAX(ObserveTime) AS maxTime
                    FROM `observe_datum`
                WHERE 1
                    AND `StationID` LIKE '46%'
                GROUP BY `StationID`
              ) sub, `observe_datum` AS main
              WHERE 1
                  AND sub.`StationID` = main.`StationID`
                  AND sub.maxTime = main.ObserveTime
             ORDER BY main.`ObserveTime` DESC;
    """
    db_proxy = RWProxy(db_config=db_config_path, db_label='172.17.5.165/ObserveData')
    table = db_proxy.fromdb(sql, latency=False)
    db_proxy.close()
    logger.debug(sql)
    return table


def transformtable(table):
    sql = """SELECT * FROM CWSP_weather_define;"""
    proxy = RWProxy(db_config=db_config_path, db_label='localhost/CRSdb')
    logger.info(sql)
    weather_define_map = dict()
    for dic in proxy.fromdb(sql).dicts():
        weather_define_map[dic['Weather_zhtw']] = dic
    proxy.close()

    map = {
        "Code": None,
        "Weather_enus": "No Weather Description",
        "Weather_zhtw": u"無天氣描述"
    }
    dicts = []
    for dic in table.dicts():
        text = dic['Weather_zhtw']
        data = weather_define_map.get(text) or map
        dic.update(data)
        dicts.append(dic)
    table = petl.wrap(petl.fromdicts(dicts))
    return table


def load(table):
    proxy = RWProxy(db_config=db_config_path, db_label='localhost/CRSdb')
    num = proxy.todb(table, table_name='observe_datum', mode='update', duplicate_key=('StationID', 'ObserveTime'))
    proxy.close()
    return num


if __name__ == '__main__':
    db_config_path = os.path.join(os.path.expanduser('~'), 'cfg', 'db_config.yaml')
    log_file_path = os.path.join(os.path.expanduser('~'), 'log', 'import_observe_datum.%s' % time.strftime('%Y%m%d'))
    logging.basicConfig(
        level=getattr(logging, 'DEBUG'),
        filename=log_file_path,
        format="[%(levelname)s][%(asctime)s] %(message)s"
    )
    logger = logging.getLogger('import_observe_datum')
    try:
        table = extract()
        table = transformtable(table)
        num = load(table)
    except Exception:
        logger.error(traceback.format_exc())
