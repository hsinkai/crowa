#-*- coding: utf-8 -*-

import os.path
import re

class group_module():
    
    def __init__(self, event, filename):
        self.mat = re.match(os.path.expandvars(event), os.path.expandvars(filename))
        if self.mat != None:
            self.group = ('',) + self.mat.groups()
        else:
            self.group = None
            
    def match(self):
        return self.mat
    
    def groups(self):
        return self.group

    def is_group(self):
        
        if self.mat.lastindex == None:
            return 0
        else:
            return 1
    
    def sub(self, filename):
        return re.sub(r'\\\d', lambda m: self.group[int(m.group(0)[1])], os.path.expandvars(filename))