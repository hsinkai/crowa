#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import re
from datetime import datetime
from datetime import timedelta
import collections
from math import radians, cos, sin, asin, sqrt
import traceback
import threading

import petl

import lib

PROJECT_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../')) 
HOME = os.path.expanduser("~")

def dis(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
     on the earth (specified in decimal degrees)
     """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km
            
def search_min(lon, lat, sequence, left, right):
    value, distance, index = None, sys.maxint, None
    while left <= right:
        d = dis(lon, lat, sequence[left][0], sequence[left][1])
        if d < distance:
            distance = d
            value = sequence[left][2]
        left += 1
    return value
  
  
def load(filename):
    sequence = petl.fromtext(filename).skip(1
                ).setheader(['lines']
                ).split('lines', '\s+'
                ).setheader(['lon', 'lat', 'value']
                ).convertall(float
                ).select("115 < {lon} < 125 and 20 < {lat} < 28"
                ).tuple()
    return sequence[1:]  #  skip header
        
        

class NWW3_WRF():
    sample = petl.fromcsv(os.path.join(HOME, 'var/Points')).tuple()[1:]
    def __init__(self, src_path, str_datetime, log, dataPool):
        self.log           = log
        self.src_path      = src_path
        self.str_datetime      = str_datetime
        self.ftype_pattern = re.compile(r".+-(dir|hs|fhs|fd)\..+")
        self.workdir = os.path.join(dataPool, str_datetime)
        self.data = list()
        self.orderedFiles = None
        
    def extract(self):
        self.log.write('Do %s' % (self.src_path), 'debug')
        try:
            self._decompress()
            self._ordergroup()
            self._extract()
        except RuntimeError as e:
            self.log.write('wrf: %s' % str(e))
        except Exception as e:
            self.log.write(traceback.format_exc())
     
    def _decompress(self):
        cmd = "tar -C {dest} -xf {source} *-dir* *-hs* *-fhs*  *-fd* ".format(source=self.src_path, dest=self.workdir)   
        if os.path.exists(self.workdir):
            if 0 != os.system("rm -rf %s" % os.path.join(self.workdir, "*")):
                raise RuntimeError("can not clean: %s" % self.workdir)
        else:   
            os.makedirs(self.workdir)
  
        if 0 != os.system(cmd):
            raise RuntimeError("decompress error: %s" % cmd)
         
    def _ordergroup(self):
        self.fileGroups = collections.defaultdict(dict)
        for fpath in os.listdir(self.workdir):
            tau = fpath [-3:]
            filetype, = self.ftype_pattern.match(fpath).groups()
            self.fileGroups[tau][filetype] = fpath 
        self.orderedFiles = collections.OrderedDict(sorted(self.fileGroups.items()))  
    
    def _fetch_data(self, dt, fdir, fhs, ffhs, ffd):
        dir_file = load(os.path.join(self.workdir, fdir))
        hs_file  = load(os.path.join(self.workdir, fhs))
        fhs_file = load(os.path.join(self.workdir, ffhs))
        fd_file  = load(os.path.join(self.workdir, ffd))
        sub_table = list()
        for type, no, lon, lat, ncpos  in self.sample:
            lon, lat = float(lon), float(lat)
            sub_table.append({'type' : type, 
                               'no'  : no, 
                               'time': dt, 
                               'lon' : lon, 
                               'lat' : lat, 
                               'dir' : search_min(lon, lat, dir_file, 0, len(dir_file)-1), 
                               'hs'  : search_min(lon, lat, hs_file,  0, len(hs_file)-1), 
                               'fhs' : search_min(lon, lat, fhs_file, 0, len(fhs_file)-1), 
                               'fd'  : search_min(lon, lat, fd_file,  0, len(fd_file)-1),
                            })
            
        return sub_table  
    
    def _extract(self):
        d = self.str_datetime
        issuet = datetime(2000+int(d[0:2]), int(d[2:4]), int(d[4:6]), int(d[6:8])) ##yyyymmddHH
        for order, files in self.orderedFiles.items(): ## tau, filePaths
            dt = issuet + timedelta(hours=int(order)+8-2) ## utcTime to taipeiTime #put 8 to 6 for web display
            sub_table = self._fetch_data(dt, files['dir'], files['hs'], files['fhs'], files['fd'])
            self.data.extend(sub_table)
    
    def transform(self):
        self.table = petl.fromdicts(self.data, header=self.data[0].keys())
        
        
    def load(self, writer):
        writer(self.table, 'Wave', mode='append')

def main(src_path): 
    home = os.path.expanduser("~")
    #m = re.match(r".+NWW3-WRF\.(\d{8})\.tar", src_path)          
    m = re.match(r".+NWW3-WRF\.([\d]{8}).tar", src_path)
    str_datetime, = m.groups()
    wrf = NWW3_WRF( src_path, 
                    str_datetime, 
                    log=lib.log_module.log_module(os.path.join(home, 'log', 'dbImport')), 
                    dataPool='/CRSdata/dataPool/Ocean/NWW3/'
                )

    wrf.extract()
    wrf.transform()
    wrf.load(lib.db.DBWriter)
    

'''Usage:  python wave.py file_path'''   
if __name__ == "__main__":   
    main(sys.argv[-1])
    
