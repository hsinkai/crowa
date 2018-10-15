#!/home/crsadm/.conda/envs/crs-py27/bin/python
# coding=utf-8

import sys
import subprocess
import re
import os

basedir = os.path.dirname(os.path.abspath(__file__))

jsonbuilder = os.path.join(basedir, 'jsonbuilder.py')
pushnote = os.path.join(basedir, 'pushnote.py')
unzip = os.path.join(basedir, 'unzip.py')


if __name__ == '__main__':
    do = False
    if sys.argv[1] in ('GT', 'StationDaylight', 'Tide', 'AquaCulture'):
        subprocess.Popen([jsonbuilder, sys.argv[1]])
        do = True

    if re.match(r'.*(\d+)_48hrsSeaObs.zip', sys.argv[-1]):
        # from cwsp.conf import context
        # context.init_config(cfg_path)
        # subprocess.Popen(['python', unzip, sys.argv[1], '-target', context.config['WORK_DIR']])
        subprocess.Popen([jsonbuilder, sys.argv[-1]])
        do = True

    if re.match(r'.*MMC-recreation.xml', sys.argv[-1]):
        p = subprocess.Popen(['/home/crsadm/bin/dbImport/xml2csv.py', sys.argv[-3], '-f', sys.argv[-1]])
        p.wait()
        subprocess.Popen([jsonbuilder, 'OCM3'])
        do = True

    if sys.argv[1] == 'AquaCulture':
        subprocess.Popen(['/home/crsadm/bin/cwsp-1.0/bin/pushnote.py', sys.argv[1]])
        do = True

    if not do:
        print "Given target '%s' is invalid, it should be {'GT', 'StationDaylight', 'Tide', 'AquaCulture', 'SeaCondition'}" % sys.argv[1]
