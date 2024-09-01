'''
JSON読み取りに関する関数定義  
ここでは, json.loadによって読取った辞書に関する関数を定義.
'''
from PyPrologue.app.CommandLine import *

def GetValue(json : dict, *keys):
    '''
    json.loadによって読取った辞書から値を取得する
    Args:
        json : json.loadによって読取った辞書.
        keys : キー (上位から順に入力. e.g., simulation.dt -> GetValue(json, "simulation", "dt"))
    '''
    dict_buff : dict = json
    hasKey = True
    
    for key in keys:
        if key in dict_buff:
            dict_buff = dict_buff[key]
        else:
            hasKey = False
            break
    
    if not hasKey:
        print(keys)
        PrintInfo(PrintInfoType.Error, 
            "The key of " + ".".join((keys)) + " has no value." )
        raise KeyError
    
    return dict_buff