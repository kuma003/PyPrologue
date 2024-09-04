'''
rocketファイルデバッグ用コード
'''
#--------------------------------PyPrologueをインポートするための処理--------------------------------#
import sys; import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # モジュール検索パス追加
os.chdir(os.path.join(os.path.dirname(__file__), '..')) # カレントディレクトリ変更
#------------------------------------------------終了-----------------------------------------------#

from PyPrologue.rocket.RocketSpec import *
import json

from pprint import pprint

print("------------------------------\n")
file = "input/spec/spec_multi.json"
print(f"filepath : {file}")
with open(file) as f:
    spec_dict = json.load(f)
    rocket_spec = RocketSpecification(spec_dict)
    pprint(rocket_spec.__dict__, width=40)

print("------------------------------\n")
file = "input/spec/spec_single.json"
print(f"filepath : {file}")
with open(file) as f:
    spec_dict = json.load(f)
    rocket_spec = RocketSpecification(spec_dict)
    pprint(rocket_spec.__dict__)
    
    
print("------------------------------\n")
file = "input/spec/NSE2024_spec_single_第3版.json"
print(f"filepath : {file}")
with open(file) as f:
    spec_dict = json.load(f)
    rocket_spec = RocketSpecification(spec_dict)
    pprint(rocket_spec.__dict__, width=40)
    
print("------------------------------\n")

# comment : pprintでも綺麗に出力できなかった...