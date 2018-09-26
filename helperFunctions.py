def formQueryString(arrayOfObjects):
    qrystr_new = {}
    if len(arrayOfObjects)>0:
        qrystr = "" 
        for key_values in arrayOfObjects:
            for key,item in key_values.items():
                qrystr+='"%s":%s,'%(key,item)
                qrystr_new.update({key:item})
        qrystr_final = qrystr[:-1]                  
    return qrystr_new
    

        
def get_cdets_count_old(arrayOfObjects):
    bugids_array = []
    if arrayOfObjects:
        for key,values in enumerate(arrayOfObjects):
            for key,item in values.items():
                if key == "cdets" and item.strip()!="":
                    bugids_array.append(item)
    return bugids_array

def get_cdets_count(arrayOfObjects):
    bugids_array = []
    if arrayOfObjects:
        for key,values in enumerate(arrayOfObjects):
            for key,item in values.items():
                if key == "cdets" and item.strip()!="":
                    splitted_colon_cdets=item.split(';')
                    splitted_comma_cdets=item.split(',')
                    splitted_space_cdets=item.split(' ')                    
                    if len(splitted_colon_cdets)>1:
                        for entry in item.split(';'):
                            if entry!= '':
                                bugids_array.append(entry)
                    elif len(splitted_comma_cdets)>1:
                        for entry in item.split(','):
                            if entry!= '':
                                bugids_array.append(entry)
                    elif len(splitted_space_cdets)>1:
                        for entry in item.split(' '):
                            if entry!= '':
                                bugids_array.append(entry)                              
                    else:                   
                        bugids_array.append(item)
    return bugids_array 
    
def get_splitted_cdets(arrayOfObjects):
    bugids_array = []
    if arrayOfObjects:
        for key,item in enumerate(arrayOfObjects):
            splitted_colon_cdets=item.split(';')
            splitted_comma_cdets=item.split(',')
            splitted_space_cdets=item.split(' ')                    
            if len(splitted_colon_cdets)>1:
                for entry in item.split(';'):
                    if entry!= '':
                        bugids_array.append(entry)
            elif len(splitted_comma_cdets)>1:
                for entry in item.split(','):
                    if entry!= '':
                        bugids_array.append(entry)
            elif len(splitted_space_cdets)>1:
                for entry in item.split(' '):
                    if entry!= '':
                        bugids_array.append(entry)                              
            else:                   
                bugids_array.append(item)
    return bugids_array