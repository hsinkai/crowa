#-*- coding: utf-8 -*-
import sys
import os
import re
import shutil
import subprocess
import pyinotify
import getopt
import time
import signal
from lib.log_module import log_module
from lib.group_module import group_module

global log_handler, poller_config_content

def handleSIGCHLD(signum, frame):
    os.waitpid(-1, os.WNOHANG)

def event_processing(event):

    global log_handler, poller_config_content
    msg = 'Receive : %s' % event.pathname  
    log_handler.write(msg)
    
    file_name = os.path.basename(event.pathname)
    dir_name = os.path.dirname(event.pathname)
    
    file_should_be_remove = 0  
    
    #read config information 
    for i in range(0, len(poller_config_content)):
        source_dir = poller_config_content[i].source_dir
        regex_file_name = poller_config_content[i].regex_file_name
        dest_dir = poller_config_content[i].dest_dir
        dest_file_name = poller_config_content[i].dest_file_name                 
        fork_proc = poller_config_content[i].fork_proc
        #decide file satisfied config content
        if dir_name == source_dir and re.search(regex_file_name, file_name):
            #decide file need move
            if dest_dir != '#':
                if dest_file_name != '#':
                    modified_dest_file_name = dest_file_name
                else :
                    modified_dest_file_name = file_name
                try :
                    shutil.copy2(os.path.join(source_dir, file_name), os.path.join(dest_dir, modified_dest_file_name))
                    msg = 'move file : %s to : %s' % (os.path.join(source_dir, file_name), os.path.join(dest_dir, modified_dest_file_name))
                    log_handler.write(msg)
                    file_should_be_remove = 1
                except :
                    msg = '[ERROR] can not move file : %s to : %s' % (os.path.join(source_dir, file_name), os.path.join(dest_dir, modified_dest_file_name))
                    log_handler.write(msg)
                    continue
                #decide need fork other process
                if fork_proc != '#':
                    regex_group_handler = group_module(regex_file_name, file_name)
                    if regex_group_handler.is_group() == 1:
                        cmd = regex_group_handler.sub(fork_proc)
                    else:
                        arg_file_path = os.path.join(dest_dir, modified_dest_file_name)
                        cmd =  fork_proc + ' ' + arg_file_path
                    try:
                        pipe = subprocess.Popen(cmd.split())
                        msg = 'fork process : [%s] %s' % (pipe.pid, cmd)
                        log_handler.write(msg)
                    except:
                        msg = '[ERROR] fork process fail : [%s] %s' % (pipe.pid, cmd)
                        log_handler.write(msg)                        
            elif fork_proc != '#':
                regex_group_handler = group_module(regex_file_name, file_name)
                if regex_group_handler.is_group() == 1:
                    cmd = regex_group_handler.sub(fork_proc)
                else:
                    cmd =  fork_proc + ' ' + event.pathname
                try:
                    pipe = subprocess.Popen(cmd.split())
                    msg = 'fork process : [%s] %s' % (pipe.pid, cmd)
                    log_handler.write(msg)
                except:
                    msg = '[ERROR] fork process fail : [%s] %s' % (pipe.pid, cmd)
                    log_handler.write(msg)                       
                
    #the file had been moved         
    if file_should_be_remove == 1 :
        try :
            os.remove(event.pathname)
        except :
            msg = '[ERROR] can not remove file : %s' % event.pathname  
            log_handler.write(msg)

    
class poller_info(object):
    def __init__(self, source_dir, regex_file_name, dest_dir, dest_file_name, fork_proc):
        self.source_dir = source_dir
        self.regex_file_name = regex_file_name
        self.dest_dir = dest_dir
        self.dest_file_name = dest_file_name
        self.fork_proc = fork_proc
        
#define inotify event 
class MyEventHandler(pyinotify.ProcessEvent):

    #writtable file was closed
    def process_IN_CLOSE_WRITE(self, event): 
        event_processing(event)
    
    #file has been moved to the directory
    def process_IN_MOVED_TO(self, event): 
        event_processing(event)
        
class MyEventWatcher(pyinotify.ProcessEvent):

    #watch all inotify event
    def process_default(self, event):
        print event
        
def is_file_mtime_in_range(current_time, time_offset, file_path):
    
    file_property = os.stat(file_path)
    
    if file_property.st_mtime >= (current_time - time_offset): 
        return 1
    else:
        return 0       

def proc_without_inotify_file(file_path, poller_config_index):
    
    #proc file that poller without receive the inotify 
    
    global log_handler, poller_config_content
    msg = 'Receive by time offset : %s' % file_path
    log_handler.write(msg)
    
    file_name = os.path.basename(file_path)
    dir_name = os.path.dirname(file_path)
    
    file_should_be_remove = 0  
    
    #read config information 
    #for i in range(0, len(poller_config_content)):
    source_dir = poller_config_content[poller_config_index].source_dir
    regex_file_name = poller_config_content[poller_config_index].regex_file_name
    dest_dir = poller_config_content[poller_config_index].dest_dir
    dest_file_name = poller_config_content[poller_config_index].dest_file_name       
    fork_proc = poller_config_content[poller_config_index].fork_proc
    #decide file satisfied config content
    if dir_name == source_dir and re.search(regex_file_name, file_name):
        #decide file need move
        if dest_dir != '#':
            if dest_file_name != '#':
                modified_dest_file_name = dest_file_name
            else :
                modified_dest_file_name = file_name
            try :
                shutil.copy2(os.path.join(source_dir, file_name), os.path.join(dest_dir, modified_dest_file_name))
                msg = 'move file : %s to : %s' % (os.path.join(source_dir, file_name), os.path.join(dest_dir, modified_dest_file_name))
                log_handler.write(msg)
                file_should_be_remove = 1
            except :
                msg = '[ERROR] can not move file : %s to :%s' % (os.path.join(source_dir, file_name), os.path.join(dest_dir, modified_dest_file_name))
                log_handler.write(msg)
                return 1
            #decide need fork other process
            if fork_proc != '#':
                regex_group_handler = group_module(regex_file_name, file_name)
                if regex_group_handler.is_group() == 1:
                    cmd = regex_group_handler.sub(fork_proc)
                else:
                    arg_file_path = os.path.join(dest_dir, modified_dest_file_name)
                    cmd =  fork_proc + ' ' + arg_file_path
                try:
                    pipe = subprocess.Popen(cmd.split())
                    msg = 'fork process : %s' % cmd
                    log_handler.write(msg)
                except:
                    msg = '[ERROR] fork process fail : %s' % cmd
                    log_handler.write(msg)   
        elif fork_proc != '#':
            regex_group_handler = group_module(regex_file_name, file_name)
            if regex_group_handler.is_group() == 1:
                cmd = regex_group_handler.sub(fork_proc)
            else:
                cmd =  fork_proc + ' ' + file_path
            try:
                pipe = subprocess.Popen(cmd.split())
                msg = 'fork process : %s' % cmd
                log_handler.write(msg)
            except:
                msg = '[ERROR] fork process fail : %s' % cmd
                log_handler.write(msg)   
                
    #the file had been moved         
    if file_should_be_remove == 1 :
        try :
            os.remove(file_path)
        except :
            msg = '[ERROR] can not remove file : %s' % file_path  
            log_handler.write(msg)
    
################################################## main ##############################################################
def main():
    
    #signal.signal(signal.SIGCHLD, signal.SIG_IGN)
    signal.signal(signal.SIGCHLD, handleSIGCHLD)
    
    global log_handler, poller_config_content
    
    HOME = os.path.expanduser("~")
    poller_config_path = HOME + '/cfg/Poller.cfg'
    poller_log_path = HOME + '/log/Poller'
    time_offset = 0
    enable_event_watcher = 0
    
    current_time = time.time()
    current_time = round(current_time)
    
    try:  
        opts, args = getopt.getopt(sys.argv[1:], "hwl:f:o:")  
    except getopt.GetoptError:  
        print 'invalid option'
        print 'Try `-h` for more information.'
        sys.exit(1)
        
        
    for opt, arg in opts:  
        if opt in ('-h'):  
            print('Usage: python Poller [options]')
            print('')
            print('options:')
            print('    -h usage                  help')
            print('    -f config                 name of configuration file')
            print('    -l log_path               pathname of log file')
            print('    -o time_offset(sec)       offset before current time(sec)')
            print('    -w watch                  watch inotify event')    
            sys.exit(0) 
        if opt in ('-f'):  
            poller_config_path = arg
            continue
        if opt in ('-l'):  
            poller_log_path = arg
            continue
        if opt in ('-o'):  
            time_offset = int(arg)
            continue
        if opt in ('-w'):  
            enable_event_watcher = 1
            continue    
    
    
    log_handler = log_module(poller_log_path)
    
    msg = '[START] Poller start'
    log_handler.write(msg)
    
    poller_config_file = open(poller_config_path ,'r')
    inotify_watch = pyinotify.WatchManager()
    poller_config_content = []
    
    #read config file and save the information
    for line in poller_config_file :
        if line.startswith('#') == 0 and line.startswith('\n') == 0 :
            parse_line = line.split()
            read_poller_info = poller_info('','','','','') 
            read_poller_info.source_dir = parse_line[0]
            read_poller_info.source_dir = os.path.expandvars(read_poller_info.source_dir)
            read_poller_info.regex_file_name = parse_line[1]
            read_poller_info.dest_dir = parse_line[2]
            read_poller_info.dest_dir = os.path.expandvars(read_poller_info.dest_dir)
            read_poller_info.dest_file_name = parse_line[3]
            read_poller_info.fork_proc = parse_line[4]
            if len(parse_line) > 4 :
                for i in range(5,len(parse_line)) :
                    read_poller_info.fork_proc = read_poller_info.fork_proc + ' ' + parse_line[i]
            poller_config_content.append(read_poller_info)
    #add inotify watch
            inotify_watch.add_watch(read_poller_info.source_dir, pyinotify.ALL_EVENTS, rec=True)      
    poller_config_file.close()
    
    '''
    print len(poller_config_content)
    for i in range(0, len(poller_config_content)) :
        print poller_config_content[i].source_dir
        print poller_config_content[i].regex_file_name
        print poller_config_content[i].dest_dir
        print poller_config_content[i].dest_file_name
        print poller_config_content[i].fork_proc
    '''
    
    #if time_offset greater than zero
    #proc in range file 
    if time_offset > 0:
        for i in range(0, len(poller_config_content)):
            for dirpath, dirnames, filenames in os.walk(poller_config_content[i].source_dir):
                for filename in filenames:
                    try:                    
                        if (is_file_mtime_in_range(current_time, time_offset, os.path.join(dirpath, filename)) == 1):
                            proc_without_inotify_file(os.path.join(dirpath, filename), i)
                    except:
                        continue
                        
    #start inotify watcher
    if enable_event_watcher == 1:
        inotify_event_handler = MyEventWatcher()
    else:        
        inotify_event_handler = MyEventHandler()
    notifier = pyinotify.Notifier(inotify_watch, inotify_event_handler)
    notifier.loop()
    
if __name__ == "__main__":
    main()