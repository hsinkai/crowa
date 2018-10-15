#!/home/crsadm/.conda/envs/crs-py27/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import datetime
import logging

from dateutil import parser
from xml.etree.ElementTree import parse
import petl

raise SystemExit()

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, basedir)

from cwsp.conf import Context, CONFIG_ENVAR_PATH, HOME


def extract(profile, workdir):
    dicts = []
    outer = parse(profile)
    station_ids = outer.findall('./stationID')
    updatetime_str = outer.getroot().attrib.get('updatetime')
    modify_time = parser.parse(updatetime_str, ignoretz=True) if updatetime_str else datetime.datetime.now()
    for station_id_tree in station_ids:
        status = station_id_tree.find('./status')
        if status is not None and status.find('./station') is not None:
            if status.find('./station').text.strip().startswith(u'無觀測'):
                continue
        profile = station_id_tree.find('./profile')
        station_id = station_id_tree.attrib['id'].strip()
        # filename = station_id + '.xml'
        outer_data = {
            'station_id': station_id,
            'seas_chName': profile.find('./seas_chName').text.strip(),
            'latitude': float(profile.find('./latitude').text.strip()),
            'longitude': float(profile.find('./longitude').text.strip()),
            'chName': getattr(profile.find('./chName'), 'text', None) and profile.find('./chName').text.strip(),
            'chCity': getattr(profile.find('./chCity'), 'text', None) and profile.find('./chCity').text.strip(),
            'kind_chName': getattr(profile.find('./kind_chName'), 'text', None) and profile.find('./kind_chName').text.strip(),
            'chTown':  getattr(profile.find('./chTown'), 'text', None) and profile.find('./chTown').text.strip(),
            'chLocation': getattr(profile.find('./chLocation'), 'text', None) and profile.find('./chLocation').text.strip(),
            'dataItem': getattr(profile.find('./dataItem'), 'text', None) and profile.find('./dataItem').text.strip(),
          #  'file_path': (workdir + filename) if workdir.endswith('/') else ('%s/%s' % (workdir, filename)),
            'modifytime': modify_time,
            'updatetime': datetime.datetime.now(),
        }
        dicts.append(outer_data)
    return petl.wrap([row for row in petl.fromdicts(dicts)])


def load(table):
    from dbman import RWProxy
    db_proxy = RWProxy(db_config=os.path.join(HOME, 'cfg', 'db.yaml'), db_label='61.60.103.175/CRSdb')
    db_proxy.todb(table, table_name='meta_sea_station_profile', mode='update', duplicate_key=('station_id', ))
    for sql in db_proxy.writer.make_sql():
        Context.logger.info(sql)
    db_proxy.close()


if __name__ == '__main__':
    # parse commandline
    default_workdir = '/CRSdata/dataPool/MAROBS'
    # default_workdir = r'E:/CRS/cwsp/workspace/aaa/'
    default_log_path = "sea_station_profile_parser." + datetime.datetime.now().strftime('%Y%m%d')

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('xml', help=u"上游及時海況資料包")
    arg_parser.add_argument('-f', default=None, help=u"指定設定檔，預設取環境變數 $%s。" % CONFIG_ENVAR_PATH)
    arg_parser.add_argument('-datapool', default=default_workdir, help=u"DataPool目錄, 預設：%s" % default_workdir)
    arg_parser.add_argument('-log', default=default_log_path, help=u'記錄檔路徑, 預設：%s' % default_log_path)
    args = arg_parser.parse_args()

    Context.init_config(config_path=args.f)
    Context.init_logger(name=__file__, filename=args.log)
    Context.logger.addHandler(logging.StreamHandler())
    Context.logger.info('Received: %s' % args.xml)

    table = extract(args.xml, args.datapool)
    load(table)
