import sys
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from fileinput import filename
import re
import shutil
import datetime
import time
from time import mktime
from time import strftime
import heapq
#import calendar
#from test.pystone import Char1Glob

class time_spec(object):
    def __init__(self, stamp_head, stamp_tail, stamp_type):
        self.stamp_head = stamp_head
        self.stamp_tail = stamp_tail
        self.stamp_type = stamp_type
        
        
class time_list(object):
    def __init__(self, year_num, month_num, day_num, year_day, hour_num, min_num, sec_num):
        self.year_num = year_num
        self.month_num = month_num
        self.day_num = day_num
        self.year_day = year_day
        self.hour_num = hour_num
        self.min_num = min_num        
        self.sec_num = sec_num


#0 1 2 3 4 5 6#
#Y M D J H m s#
list_time_spec = []
    
for i in range(7) :
    list_time_spec.append(time_spec(0,0,0))


month_list = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def str_only (str_src):
    str_src = str_src.strip('\n')
    str_src = str_src.strip()
    
    return str_src

def find_date_name (date_name):
    
    sym_count = date_name.count('/')
    find_count = 0
    head_str = ''
    new_str = ''

    if sym_count == 0 :
        return '', date_name
    else :
        for char in date_name :
            if find_count  < sym_count :
                head_str = head_str + char
            if char == '/' :
                find_count = find_count + 1
            if find_count == sym_count and char != '/' :
                new_str = new_str + char
    
    return head_str, new_str
                
            

def find_time_spec (list_test):
    
    global list_time_spec
    final_pattern = ''
    if list_test.count('~') != 0 and list_test.count('~')%2 == 0 :
        find_pattern_num = 0
        index_pattern = 0
        is_head = 0
        is_tail = 0
        
        org_str = list_test.replace('~', '')
        org_str = org_str.replace('^', '')
        
        for i in range(7) :
            list_time_spec[i] = time_spec('0', '0', '0')
        
        
        for char in list_test :           
            if char == '~' :
                find_pattern_num = find_pattern_num + 1
                if find_pattern_num % 2 == 1 :
                    is_head = index_pattern 
                elif find_pattern_num % 2 == 0 :
                    is_tail = index_pattern 
                    temp_pattern = list_test[is_head+1 : is_tail]                   
                                  
                    if temp_pattern.find('YYYY') != -1 :
                        stamp_index = org_str.find('YYYY')
                        list_time_spec[0] = time_spec(stamp_index, stamp_index+4, 'YYYY')
                        temp_pattern = temp_pattern.replace('YYYY', '[0-9][0-9][0-9][0-9]')
                    elif temp_pattern.find('YY') != -1 :
                        stamp_index = org_str.find('YY')
                        list_time_spec[0] = time_spec(stamp_index, stamp_index+2, 'YY')
                        temp_pattern = temp_pattern.replace('YY', '[0-9][0-9]')
                    elif temp_pattern.find('Y') != -1 :
                        stamp_index = org_str.find('Y')
                        list_time_spec[0] = time_spec(stamp_index, stamp_index+1, 'Y') 
                        temp_pattern = temp_pattern.replace('Y', '[0-9]')
                        
                    if temp_pattern.find('MM') != -1 :
                        stamp_index = org_str.find('MM')
                        list_time_spec[1] = time_spec(stamp_index, stamp_index+2, 'MM')
                        temp_pattern = temp_pattern.replace('MM', '[0-9][0-9]')
                    elif temp_pattern.find('M', 0, len(temp_pattern)) == 0 :
                        stamp_index = org_str.find('M')
                        list_time_spec[1] = time_spec(stamp_index, stamp_index+1, 'M')
                        temp_pattern = temp_pattern.replace('M', '[0-9abcABC]')
                        
                    if temp_pattern.find('DD') != -1 :
                        stamp_index = org_str.find('DD') 
                        list_time_spec[2] = time_spec(stamp_index, stamp_index+2, 'DD')
                        temp_pattern = temp_pattern.replace('DD', '[0-9][0-9]') 
            
                    if temp_pattern.find('JJJ') != -1 :
                        stamp_index = org_str.find('JJJ')
                        list_time_spec[3] = time_spec(stamp_index, stamp_index+3, 'JJJ')
                        temp_pattern = temp_pattern.replace('JJJ', '[0-9][0-9][0-9]')
                        
                    if temp_pattern.find('HH') != -1 :
                        stamp_index = org_str.find('HH') 
                        list_time_spec[4] = time_spec(stamp_index, stamp_index+2, 'HH')
                        temp_pattern = temp_pattern.replace('HH', '[0-9][0-9]')
                        
                    if temp_pattern.find('mm') != -1 :
                        stamp_index = org_str.find('mm') 
                        list_time_spec[5] = time_spec(stamp_index, stamp_index+2, 'mm')
                        temp_pattern = temp_pattern.replace('mm', '[0-9][0-9]')
                        
                    if temp_pattern.find('ss') != -1 :
                        stamp_index = org_str.find('ss') 
                        list_time_spec[6] = time_spec(stamp_index, stamp_index+2, 'ss')
                        temp_pattern = temp_pattern.replace('ss', '[0-9][0-9]') 
                    
                    final_pattern = final_pattern + temp_pattern
            
            elif find_pattern_num % 2 == 0 : 
                final_pattern = final_pattern + char     
            
            index_pattern = index_pattern + 1
    
    else :
        logger.info("[ERROR] sym '~' should a pair")
    
    return final_pattern

def cul_real_time (time_test):
    
    global list_time_spec
    
    cul_time = time_list(0, 0, 0, 0, 0, 0, 0)
    now_time = time_list(0, 0, 0, 0, 0, 0, 0)
    JJJ_to_month = 0
    JJJ_to_day = 0

    if list_time_spec[0].stamp_type == 'YYYY':
        try:
            cul_time.year_num = int (time_test[list_time_spec[0].stamp_head : list_time_spec[0].stamp_tail], 10)
        except :
            return -1

    elif list_time_spec[0].stamp_type == 'YY':
        try :
            now_time.year_num = int(time.strftime("%Y"), 10)
            cul_time.year_num = int (time_test[list_time_spec[0].stamp_head : list_time_spec[0].stamp_tail], 10)
            cul_time.year_num = cul_time.year_num + now_time.year_num/100 *100
            if cul_time.year_num > now_time.year_num :
                cul_time.year_num = cul_time.year_num - 100
        except :
            return -1
    elif list_time_spec[0].stamp_type == 'Y':
        try :
            now_time.year_num = int(time.strftime("%Y"), 10)
            cul_time.year_num = int (time_test[list_time_spec[0].stamp_head : list_time_spec[0].stamp_tail], 10)
            cul_time.year_num = cul_time.year_num + now_time.year_num/10 *10
            if cul_time.year_num > now_time.year_num :
                cul_time.year_num = cul_time.year_num - 10
        except :
            return -1
            
    if list_time_spec[1].stamp_type == 'MM':
        try :
            cul_time.month_num = int (time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail], 10)
        except :
            return -1  

    elif list_time_spec[1].stamp_type == 'M':
        try : 
            if time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail] == 'a' or time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail] == 'A' :
                cul_time.month_num = 10
            elif time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail] == 'b' or time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail] == 'B' :    
                cul_time.month_num = 11
            elif time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail] == 'c' or time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail] == 'C' :    
                cul_time.month_num = 12
            else :
                cul_time.month_num = int (time_test[list_time_spec[1].stamp_head : list_time_spec[1].stamp_tail], 10)
        except :
            return -1
               
                    
    if list_time_spec[2].stamp_type == 'DD':
        try :
            cul_time.day_num = int (time_test[list_time_spec[2].stamp_head : list_time_spec[2].stamp_tail], 10)
        except :
            return -1 
            
    if list_time_spec[3].stamp_type == 'JJJ':
        try :
            now_time.year_num = int(time.strftime("%Y"), 10)
            cul_time.year_day = int (time_test[list_time_spec[3].stamp_head : list_time_spec[3].stamp_tail], 10)
            if list_time_spec[0].stamp_type == '0' :
                cul_time.year_num = now_time.year_num
            for i in range(12) :
                if calendar.isleap(cul_time.year_num) and i+1 == 2 :
                    if cul_time.year_day - 29 > 0 :
                        cul_time.year_day = cul_time.year_day - 29
                    else :
                        break
                elif cul_time.year_day - month_list[i+1] > 0 :
                    cul_time.year_day = cul_time.year_day - month_list[i+1]
                else :
                    break 
                
            if list_time_spec[1].stamp_type == '0' :
                cul_time.month_num = i+1
            if list_time_spec[2].stamp_type == '0' :
                cul_time.day_num = cul_time.year_day        
        except :
            return -1                  
         
    if list_time_spec[4].stamp_type == 'HH':
        try :
            cul_time.hour_num = int (time_test[list_time_spec[4].stamp_head : list_time_spec[4].stamp_tail], 10)
        except :
            return -1
                
    if list_time_spec[5].stamp_type == 'mm':
        try :
            cul_time.min_num = int (time_test[list_time_spec[5].stamp_head : list_time_spec[5].stamp_tail], 10)
        except :
            return -1

    if list_time_spec[6].stamp_type == 'ss':
        try :   
            cul_time.sec_num = int (time_test[list_time_spec[6].stamp_head : list_time_spec[6].stamp_tail], 10)
        except :
            return -1

    
    sum_time = time.mktime((cul_time.year_num, cul_time.month_num, cul_time.day_num, cul_time.hour_num, cul_time.min_num, cul_time.sec_num, 0, cul_time.year_day, 0))
    sum_time = int(sum_time)
    return sum_time 


################################################## main ##############################################################


current = time.time()
current = round(current)

try:
    sys.argv.index('-h')
    need_help = 1
except :
    need_help = 0    

if need_help == 1 :
    print('Usage: python File_purge [options]')
    print('')
    print('options:')
    print('    -h usage          help')
    print('    -e event          remove event type')
    print('    -l logfile        pathname of logfile')
    print('    -c configfile     pathname of configfile')        
    need_help = 0
    sys.exit(0)


try :
    user_set_event = sys.argv[sys.argv.index('-e')+1] 
except :
    user_set_event = 'all'

home = os.path.expanduser("~")

try :
    fpath = sys.argv[sys.argv.index('-l')+1] 
except :
    fpath = home + '/File_purge/File_purge'
    
now_log_format = strftime('%Y%m%d')
fpath = fpath + '.' + now_log_format

logHandler = TimedRotatingFileHandler(fpath,when="midnight")
logFormatter = logging.Formatter('%(asctime)s %(name)-12s %(message)s')
logHandler.setFormatter( logFormatter )
logger = logging.getLogger( 'action' )
logger.addHandler( logHandler )

try :
    fpath = sys.argv[sys.argv.index('-c')+1] 
except :
    fpath = home + '/File_purge/File_purge.cfg'
ndm_config = open(fpath ,'r')

ndm_config.seek(0)

event_conut = 0
for line in ndm_config :
    if line.startswith('#') == 0 :
        if line.startswith('level') == 1:
            level = line.strip('level')
            level = str_only(level)
            if level == 'info' :
                logger.setLevel( logging.INFO )
            elif level == 'debug' :
                logger.setLevel( logging.DEBUG )
            else :
                logger.setLevel( logging.INFO )
                logger.info("[ERROR] undefined logger level")
                break
       
            logger.info("File_purge start")
        elif line.startswith('\n') == 0 :
            parse_line = line.split()
            abs_dir_path = parse_line[0]
            #abs_dir_path = os.path.expandvars(abs_dir_path)
            regex_file_name = parse_line[1]
            keep_time = parse_line[2]
            purge_time = parse_line[3]
            mechanism = parse_line[4]
            event_type = parse_line[5]
            logger.info("read config context  : %s %s %s %s %s %s" % (abs_dir_path, regex_file_name, keep_time, purge_time, mechanism, event_type))
            #print "read config context  : %s %s %s %s %s %s" % (abs_dir_path, regex_file_name, keep_time, purge_time, mechanism, event_type)
            keep_time = int(keep_time, 10)
            purge_time = int(purge_time, 10)
            remain_ver = keep_time
            keep_time = keep_time*3600
            purge_time = purge_time*3600
            regex_error = 0
            
            if event_type == user_set_event or user_set_event == 'all' :
                event_conut = 1
                logger.info("run event : %s" % user_set_event)
                logger.info("remove mechanism : %s" % mechanism)

                if mechanism == 'NAME' :
                    file_pattern, std_regex_file_name = find_date_name(regex_file_name)                  
                    file_pattern = file_pattern + find_time_spec (std_regex_file_name)

                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path) :]
                        for filename in filenames:
                            try :
                                if re.search(file_pattern, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    real_time = cul_real_time(filename)
                                    logger.debug("current time  : %d" % current)
                                    logger.debug("%s time = %d " % (os.path.join(dirpath, filename), real_time))
                                    if real_time != -1 and current - real_time >keep_time and current - real_time < purge_time : 
                                        try :
                                            os.remove(os.path.join(dirpath, filename))
                                            #print ('remove %s ' % os.path.join(dirpath, filename))
                                            logger.debug("remove %s" % os.path.join(dirpath, filename))
                                        except :
                                            logger.info("[ERROR] can not remove %s" % os.path.join(dirpath, filename))
                                        
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break

                elif mechanism == 'RCNTNAME' :
                    recently = 0
                    file_pattern, std_regex_file_name = find_date_name(regex_file_name)
                    file_pattern = file_pattern + find_time_spec (std_regex_file_name)

                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path) :]
                        for filename in filenames:
                            try :
                                if re.search(file_pattern, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    real_time = cul_real_time(filename)
                                    if real_time != -1 and real_time > recently :
                                        recently = real_time
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path) :]
                        for filename in filenames:
                            try :
                                if re.search(file_pattern, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    
                                    real_time = cul_real_time(filename)
                                    logger.debug("recently file time  : %d" % recently)
                                    logger.debug("%s time = %d " % (os.path.join(dirpath, filename), real_time)) 
                                    if real_time != -1 and recently - real_time >keep_time and recently - real_time < purge_time : 
                                        try :
                                            os.remove(os.path.join(dirpath, filename)) 
                                            #print('remove %s ' % os.path.join(dirpath, filename))
                                            logger.debug("remove %s" % os.path.join(dirpath, filename))
                                        except :
                                            logger.info("[ERROR] can not remove %s" % os.path.join(dirpath, filename))
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break
                                                      
                elif mechanism == 'NAMEDIR' :
                    file_pattern, std_regex_file_name = find_date_name(regex_file_name)
                    file_pattern = file_pattern + find_time_spec (std_regex_file_name)
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(file_pattern, del_abs) and abs_dir_path != dirpath :
                                nothing, std_dir_name = find_date_name(dirpath)
                                real_time = cul_real_time(std_dir_name)
                                logger.debug("current time  : %d" % current)
                                logger.debug("%s time = %d " % (dirpath, real_time))
                                if real_time != -1 and current - real_time > keep_time and current - real_time < purge_time :
                                    try :
                                        shutil.rmtree(dirpath)                         
                                        #print('remove : %s ' % dirpath)  
                                        logger.debug("remove %s" % dirpath)
                                    except :
                                        logger.info("[ERROR] can not remove %s" % dirpath)     
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break        

                elif mechanism == 'RCNTNAMEDIR' :
                    recently = 0
                    file_pattern, std_regex_file_name = find_date_name(regex_file_name)
                    file_pattern = file_pattern + find_time_spec (std_regex_file_name)
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(file_pattern, del_abs) and abs_dir_path != dirpath :
                                nothing, std_dir_name = find_date_name(dirpath)
                                real_time = cul_real_time(std_dir_name)
                                if real_time != -1 and real_time > recently :
                                    recently = real_time
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break              
                    
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(file_pattern, del_abs) and abs_dir_path != dirpath :
                                nothing, std_dir_name = find_date_name(dirpath)
                                real_time = cul_real_time(std_dir_name)
                                logger.debug("recently file time  : %d" % recently)
                                logger.debug("%s time = %d " % (dirpath, real_time))
                                if real_time != -1 and recently - real_time >keep_time and recently - real_time < purge_time :                         
                                    try :
                                        shutil.rmtree(dirpath)
                                        #print("remove : %s" % dirpath)  
                                        logger.debug("remove %s" % dirpath)
                                    except :
                                        logger.info("[ERROR] can not remove %s" % dirpath) 
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break              

                elif mechanism == 'DATE' :
                    #print 'abs_dir_path : %s' % abs_dir_path
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        #print 'abs_dir_path : %s' % abs_dir_path
                        del_abs = dirpath[ len(abs_dir_path) :]   
                        #print "del_abs : %s" % del_abs           
                        for filename in filenames:
                            try :
                                #logger.debug("file  : %s" % os.path.join(dirpath, filename))
                                #print "file  : %s" % os.path.join(dirpath, filename)
                                if re.search(regex_file_name, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    t = os.path.getmtime(os.path.join(dirpath, filename))
                                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(dirpath, filename))
                                    logger.debug("current time  : %d" % current)
                                    logger.debug("%s time = %d " % (os.path.join(dirpath, filename), mtime))
                                    if current - mtime >keep_time and current - mtime < purge_time :
                                        try : 
                                            os.remove(os.path.join(dirpath, filename))
                                            #print('remove %s ' % os.path.join(dirpath, filename))
                                            logger.debug("remove %s" % os.path.join(dirpath, filename))
                                        except :
                                            logger.info("[ERROR] can not remove %s" % os.path.join(dirpath, filename))
                                            
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break

                elif mechanism == 'RCNTDATE' :
                    recently = 0
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path) :]                        
                        for filename in filenames:
                            try :
                                if re.search(regex_file_name, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    t = os.path.getmtime(os.path.join(dirpath, filename))
                                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(dirpath, filename)) 
                                    if mtime > recently :
                                        recently = mtime
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break                     
                      
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path) :]
                        for filename in filenames:
                            try :
                                if re.search(regex_file_name, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    t = os.path.getmtime(os.path.join(dirpath, filename))
                                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(dirpath, filename))
                                    logger.debug("recently file time  : %d" % recently)
                                    logger.debug("%s time = %d " % (os.path.join(dirpath, filename), mtime))
                                    if recently - mtime >keep_time and recently - mtime < purge_time : 
                                        try :
                                            os.remove(os.path.join(dirpath, filename)) 
                                            #print('remove %s ' % os.path.join(dirpath, filename))
                                            logger.debug("remove %s" % os.path.join(dirpath, filename))
                                        except :
                                            logger.info("[ERROR] can not remove %s" % os.path.join(dirpath, filename))
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break

                elif mechanism == 'DATEDIR' :
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(regex_file_name, del_abs) and abs_dir_path != dirpath :
                                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(dirpath)
                                logger.debug("current time  : %d" % current)
                                logger.debug("%s time = %d " % (dirpath, mtime))
                                if current - mtime >keep_time and current - mtime < purge_time :                         
                                    try :
                                        shutil.rmtree(dirpath)
                                        #print('remove : %s ' % dirpath)
                                        logger.debug("remove %s" % dirpath)
                                    except :
                                        logger.info("[ERROR] can not remove %s" % dirpath)
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break
                        
                elif mechanism == 'RCNTDATEDIR' :
                    recently = 0
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(regex_file_name, del_abs) and abs_dir_path != dirpath :
                                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(dirpath)
                                if mtime > recently :
                                    recently = mtime
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break                
                    
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(regex_file_name, del_abs) and abs_dir_path != dirpath :
                                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(dirpath)
                                logger.debug("recently file time  : %d" % recently)
                                logger.debug("%s time = %d " % (dirpath, mtime))
                                if recently - mtime >keep_time and recently - mtime < purge_time :                         
                                    try :
                                        shutil.rmtree(dirpath)
                                        #print("remove : %s" % dirpath)
                                        logger.debug("remove %s" % dirpath)
                                    except :
                                        logger.info("[ERROR] can not remove %s" % dirpath)
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break                        
                    
                elif mechanism == 'VERS' :
                    file_time_list = []
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path) :]                                                
                        for filename in filenames:
                            try :
                                if re.search(regex_file_name, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    t = os.path.getmtime(os.path.join(dirpath, filename))
                                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(dirpath, filename))
                                    file_time_list.append(mtime)
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break
                    file_count = len(file_time_list)
                    file_time_list = heapq.nlargest(remain_ver,file_time_list)
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path) :]   
                        for filename in filenames:
                            try :
                                if re.search(regex_file_name, os.path.join(del_abs, filename)) and os.path.islink(os.path.join(dirpath, filename)) == 0:
                                    t = os.path.getmtime(os.path.join(dirpath, filename))
                                    (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(os.path.join(dirpath, filename))
                                    logger.debug("%s time = %d " % (os.path.join(dirpath, filename), mtime))
                                    if remain_ver < file_count:
                                        if mtime < file_time_list[remain_ver-1]: 
                                            try :
                                                os.remove(os.path.join(dirpath, filename))
                                                #print('remove %s ' % os.path.join(dirpath, filename))
                                                logger.debug("remove %s" % os.path.join(dirpath, filename))
                                            except :
                                                logger.info("[ERROR] can not remove %s" % os.path.join(dirpath, filename))
                            except :
                                logger.info("[ERROR] invalid regular expression")
                                regex_error = 1
                                break
                        if regex_error == 1 :
                            break

                elif mechanism == 'VERSDIR' : 
                    file_time_list = []
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(regex_file_name, del_abs) and abs_dir_path != dirpath :
                                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(dirpath)
                                file_time_list.append(mtime)
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break                  
                    file_count = len(file_time_list)
                    file_time_list = heapq.nlargest(remain_ver,file_time_list)                  
                    for dirpath, dirnames, filenames in os.walk(abs_dir_path):
                        del_abs = dirpath[ len(abs_dir_path)+1 :]
                        try :
                            if re.search(regex_file_name, del_abs) and abs_dir_path != dirpath:
                                t = os.path.getmtime(dirpath)
                                (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(dirpath)
                                logger.debug("%s time = %d " % (dirpath, mtime))                                
                                if remain_ver < file_count:
                                    if mtime < file_time_list[remain_ver-1]:
                                        #print("remove : %s" % dirpath) 
                                        try :
                                            shutil.rmtree(dirpath)
                                            logger.debug("remove %s" % dirpath)
                                        except :
                                            logger.info("[ERROR] can not remove %s" % os.path.join(dirpath, filename))
                        except :
                            logger.info("[ERROR] invalid regular expression")
                            regex_error = 1
                            break                           

if event_conut == 0 :
    logger.info("[WARNING] no event matched")
    