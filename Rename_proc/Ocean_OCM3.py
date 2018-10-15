#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt
import datetime

################################################## main ##############################################################
def main():
    
    result_file_path = '/CRSdata/dataPool/Ocean/OCM3_tmp'
    
    try:  
        opts, args = getopt.getopt(sys.argv[1:], "h")  
    except getopt.GetoptError:  
        print 'invalid option'
        print 'Try `-h` for more information.'
        sys.exit(1)
    
    for opt, arg in opts:  
        if opt in ('-h'):  
            print('Usage: python Ocean_OCM3 [file_name]')
            print('')
            print('options:')
            print('    -h usage                  help')
    
    
    file_name = os.path.expandvars(args[0])
    zcor_file_path = file_name.replace('hvel', 'zcor')
    hevl_file_path = file_name.replace('zcor', 'hvel')
    dir_file_path = hevl_file_path.replace('nc', 'dir')
    dir_file_path = os.path.join(result_file_path, os.path.basename(dir_file_path))
    spd_file_path = hevl_file_path.replace('nc', 'spd')
    spd_file_path = os.path.join(result_file_path, os.path.basename(spd_file_path))


    fork_time = datetime.datetime.now()
    file_date = fork_time.strftime('%Y%m%d')
    fork_time = fork_time.strftime('%Y-%m-%d %H:%M:%S')

    #cmd = '/home/crsadm/bin/sat2csv/read_ocm3_uv.exe %s %s /home/crsadm/bin/sat2csv/colorbar_spd.tab /home/crsadm/bin/sat2csv %s %s >> /home/crsadm/log/Ocean_OCM3_read_ucm3_uv.log' %(zcor_file_path, hevl_file_path, dir_file_path, spd_file_path)
    cmd = '/home/crsadm/bin/sat2csv/read_ocm3_uv.exe %s %s /home/crsadm/bin/sat2csv/colorbar_spd.tab /home/crsadm/bin/sat2csv %s %s' % (zcor_file_path, hevl_file_path, dir_file_path, spd_file_path)
    #print cmd
    log_cmd = 'echo %s [fork] %s >> /home/crsadm/log/Ocean_OCM3.%s' %(fork_time, cmd, file_date)
    os.system(log_cmd)
    os.system(cmd)
    log_cmd = 'echo %s [finish] %s >> /home/crsadm/log/Ocean_OCM3.%s' %(fork_time, cmd, file_date)
    os.system(log_cmd)




if __name__ == "__main__":
    main()
