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

file = "input/spec/spec_multi.json"
print(f"filepath : {file}")
with open(file) as f:
    spec_dict = json.load(f)
    rocket_spec = RocketSpecification(spec_dict)
    
    # ↓は参照渡し (正確には参照(id)の値渡し). メンバ変数のポインタも同じっぽい.
    body_spec : BodySpecification = rocket_spec.bodySpec(0)
    # ↓のように代入したときは新たにポインタが指定される模様.
    # body_spec = BodySpecification()
    body_spec.length = 100000

    pprint(body_spec)
    pprint(rocket_spec.bodySpec(0))

# comment : pprintでも綺麗に出力できなかった...
