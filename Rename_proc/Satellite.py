#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import getopt

################################################## main ##############################################################
def main():
    
    result_file_path = '/CRSdata/dataPool/Satellite_tmp'
    
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
    
    if file_name.find('bz2') >= 0 :
        
        copy_cmd = 'cp %s %s' %(file_name, result_file_path)
        os.system(copy_cmd)
        
        compress_file_path = os.path.join(result_file_path, os.path.basename(file_name))
        
        decompress_cmd = 'bzip2 -d %s' %compress_file_path 
        os.system(decompress_cmd)
        
        decompress_file_path = compress_file_path.replace('.bzip', '')
        decompress_file_name = os.path.basename(decompress_file_path)
        
        decompress_file_pattern = decompress_file_name.split('_')
        
        #print decompress_file_pattern
        
        date_name = decompress_file_pattern[2] + decompress_file_pattern[3]
        
        #print date_name
        
        result_file_name = (
                            decompress_file_pattern[0] + '_' + decompress_file_pattern[1] + '_' +
                            decompress_file_pattern[2] + '_' + decompress_file_pattern[3] + '_' +
                            decompress_file_pattern[4] + '_' + decompress_file_pattern[5] + '_' +
                            decompress_file_pattern[6] + '.txt'
                            )
        
        #print result_file_name
        
        txt_file_path = os.path.join(result_file_path, result_file_name)
        
        cmd = '/home/crsadm/bin/sat2csv/read_file_v2.exe %s 13 /home/crsadm/bin/sat2csv/lookup_ir.tab /CRSdata/dataPool/Satellite_tmp %s >> /dev/null' %(date_name, txt_file_path)
        #print cmd
        os.system(cmd)
                
        
    else:
        return 1




if __name__ == "__main__":
    main()
