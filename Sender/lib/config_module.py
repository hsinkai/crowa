
def get_config (config_file ,elements):
    
    config_content = {}
    file_handle = open(config_file ,'r')
    
    for element in elements :
        config_content[element] = ''
    
    for line in file_handle :
        if line.startswith('#') == 0 :
            temp = line.replace(' ','').split('=')
            if temp[0] in iter(elements) :
                config_content[temp[0]] = temp[1].strip('\n').strip()  
                
    file_handle.close()
    return config_content
    
            
            
        
        
