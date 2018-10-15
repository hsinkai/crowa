#-*- coding: utf-8 -*-
import sys
import os
import re
import shutil
import getopt
import time
from lib.log_module import log_module

################################################## main ##############################################################
def main():
    
    HOME = os.path.expanduser("~")
    compressed_file_dir = os.path.join(HOME, 'etc/Sender_compressed_file')
    log_path = os.path.join(HOME + 'log/Sender')
    client_account = os.getenv('USER')
    resend_time = 0
    resend_interval = 0
    time_out = 0
    bandwith_limit = ''
    resume = ''
    dest_dir = ''
    compress_flag = 0
    
    my_pid = os.getpid()
    
    try:  
        opts, args = getopt.getopt(sys.argv[1:], "hpcl:r:i:b:t:u:d:")  
    except getopt.GetoptError:  
        print 'invalid option'
        print 'Try `-h` for more information.'
        sys.exit(1)
        
        
    for opt, arg in opts:  
        if opt in ('-h'):  
            print('Usage: python Sender [options]...[client_ip]...[file_name]')
            print('')
            print('options:')
            print('    -h usage                  help')
            print('    -r resend_time            number of resend if failed')
            print('    -l log_path               pathname of log file')
            print('    -i resend_interval(sec)   interval of try to resend')
            print('    -b bandwith_limit(KBps)   limit the bandwidth')
            print('    -p resume                 keep partially transferred files')
            print('    -t time_out(sec)          set timeout')
            print('    -u client_account         client account name for sender login')
            print('    -d destination_directory  directory of client receive file')
            print('    -c compress file          compress file in gzip2')                  
            sys.exit(0) 
        if opt in ('-l'):  
            log_path = arg
            continue
        if opt in ('-r'):  
            resend_time = int(arg)
            continue
        if opt in ('-i'):  
            resend_interval = int(arg)
            continue
        if opt in ('-b'):
            if int(arg) > 0:  
                bandwith_limit = '--bwlimit=%d' % (int(arg))
            continue
        if opt in ('-p'):  
            resume = '-P'
            continue    
        if opt in ('-t'): 
            if int(arg) > 0: 
                time_out = int(arg)
            continue
        if opt in ('-u'):  
            client_account = arg
            continue
        if opt in ('-d'):  
            dest_dir = arg
            continue
        if opt in ('-c'):  
            compress_flag = 1
            continue
    
    log_handler = log_module(log_path)
    
    msg = '[START][%d] Sender start' % my_pid
    log_handler.write(msg)
    
    if len(args) <= 1:
        print 'missing client ip or file_path, try -h or --help for help\n'
        sys.exit(1)
    
    #get client ip and send file path    
    client_ip = os.path.expandvars(args[0])
    file_path = os.path.expandvars(args[1])
    msg = '[SEND][%d] sending : %s' % (my_pid, file_path)
    log_handler.write(msg)


    
    if os.path.isfile(file_path):
        #compress file and send to client
        if compress_flag == 1:
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            compressed_file_name = '%s_%s.tar.bz2' % (re.sub('/', '_', file_path), client_ip)
            compressed_file_path = os.path.join(compressed_file_dir, compressed_file_name)
            compress_cmd = 'tar -jcpPf %s -C %s %s' %(compressed_file_path, file_dir, file_name)
            return_value = os.system(compress_cmd)
            #check compress result
            if return_value != 0:
                msg = '[ERROR][%d] compress fail : %s' % (my_pid, compressed_file_path) 
                log_handler.write(msg)
                sys.exit(1)
        #set source file path for send
            source_file_path = compressed_file_path
        else:
            source_file_path = file_path
        #set destination path for send
        if dest_dir == '':
            dest_file_path = source_file_path
        else:
            dest_file_path = os.path.join(dest_dir, os.path.basename(source_file_path))

        send_cmd = ('rsync -prv %s %s --timeout=%d -e ssh %s %s@%s:%s'
                    % (resume, bandwith_limit, time_out, source_file_path, client_account, client_ip, dest_file_path)
                    )
        return_value = os.system(send_cmd)
        #check send result
        if return_value == 0:
            msg = '[SEND][%d] send success : %s@%s:%s' % (my_pid, client_account, client_ip, file_path) 
            log_handler.write(msg)
        else:
            msg = '[ERROR][%d] send fail : %s@%s:%s' % (my_pid, client_account, client_ip, file_path)
            log_handler.write(msg)
            #send fail, try to resend file until success or retry time over
            while(1):
                time.sleep(resend_interval)
                return_value = os.system(send_cmd)
                resend_time = resend_time - 1
                if return_value == 0:
                    msg = '[SEND][%d] send success : %s@%s:%s' % (my_pid, client_account, client_ip, file_path) 
                    log_handler.write(msg)                    
                    break
                elif  resend_time <= 0:
                    msg = '[ERROR][%d] resend fail, retry=%d : %s@%s:%s' % (my_pid, resend_time, client_account, client_ip, file_path)
                    log_handler.write(msg)
                    sys.exit(1)
                else:
                    msg = '[ERROR][%d] resend fail, retry=%d : %s@%s:%s' % (my_pid, resend_time, client_account, client_ip, file_path)
                    log_handler.write(msg)
                
                #return_value = os.system(send_cmd)
                #resend_time = resend_time - 1
                #time.sleep(resend_interval)
        #decompress client side file    
        if compress_flag == 1:
            remote_compressed_file_path = os.path.join(os.path.dirname(dest_file_path), compressed_file_name)    
            remote_decompress_cmd = ('ssh %s@%s tar -jxpPf %s -C %s' % 
            (client_account, client_ip, remote_compressed_file_path, os.path.dirname(remote_compressed_file_path)) 
            )       
            return_value = os.system(remote_decompress_cmd)
            #check decompress result
            if return_value == 0:
                msg = '[DECOMPRESS][%d] decompress success : %s@%s:%s' % (my_pid, client_account, client_ip, file_path)
                log_handler.write(msg)
                try:
                    #remove local compressed file
                    os.remove(source_file_path)
                except:
                    msg = '[ERROR][%d] can not remove compressed file : %s' % (my_pid, source_file_path)
                    log_handler.write(msg)   
                #remove client side compressed file
                remote_remove_cmd = 'ssh -f %s@%s rm %s' % (client_account, client_ip, remote_compressed_file_path)
                os.system(remote_remove_cmd)     
                                   
            else:
                msg = '[ERROR][%d] decompress fail : %s@%s:%s' % (my_pid, client_account, client_ip, file_path)
                log_handler.write(msg) 
    else:
        msg = '[ERROR][%d] is not a file : %s' % (my_pid, file_path)
        log_handler.write(msg)
        sys.exit(1)    
    
    
    
if __name__ == "__main__":
    main()
