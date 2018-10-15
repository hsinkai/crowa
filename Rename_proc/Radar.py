#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt

################################################## main ##############################################################
def main():
    
    result_file_path = '/CRSdata/dataPool/Radar_tmp'
    
    try:  
        opts, args = getopt.getopt(sys.argv[1:], "h")  
    except getopt.GetoptError:  
        print 'invalid option'
        print 'Try `-h` for more information.'
        sys.exit(1)
    
    for opt, arg in opts:  
        if opt in ('-h'):  
            print('Usage: python Radar [file_name]')
            print('')
            print('options:')
            print('    -h usage                  help')
    
    file_name = os.path.expandvars(args[0])
    
    if file_name.find('gz') >= 0 :        
        copy_cmd = 'cp %s %s' %(file_name, result_file_path)
        os.system(copy_cmd)
        
        compress_file_path = os.path.join(result_file_path, os.path.basename(file_name))
        
        decompress_cmd = 'gunzip -d %s' %compress_file_path 
        os.system(decompress_cmd)
        
        decompress_file_path = compress_file_path.replace('.gz', '')
        txt_file_path = os.path.join(result_file_path, os.path.basename(file_name).replace('gz', 'txt'))
        
        cmd = '/home/crsadm/bin/radar2csv/header2.exe %s /home/crsadm/bin/radar2csv/radar_lookuptab.txt ./ %s >> /dev/null' %(decompress_file_path, txt_file_path)
        
        os.system(cmd)
        
    else:
        return 1




if __name__ == "__main__":
    main()
