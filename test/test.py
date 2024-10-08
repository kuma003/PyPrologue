'''
デバッグ用コード
'''
from pprint import pprint

def Hoge(arg : dict):
    print(arg)

arg = {"hoge" : "foo", "hoge2": {"hogehoge": 1}}

Hoge(arg)
    