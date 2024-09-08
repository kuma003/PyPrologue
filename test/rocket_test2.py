'''
rocketファイルデバッグ用コード
'''
#--------------------------------PyPrologueをインポートするための処理--------------------------------#
import sys; import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # モジュール検索パス追加
os.chdir(os.path.join(os.path.dirname(__file__), '..')) # カレントディレクトリ変更
#------------------------------------------------終了-----------------------------------------------#

from PyPrologue.rocket.RocketSpec import *
from PyPrologue.rocket.Rocket import *
import numpy as np

from pprint import pprint

# 以下はfull関数で初期化した配列要素のid(ポインタ)がすべて同一になってしまうためアウト

print("------------------------------\n")

rocket = Rocket()
rocket.bodies = np.full(2, Body(), order="C")

print([id(body) for body in rocket.bodies]) # 全部一緒....orz

body : Body = rocket.bodies[0]
body.refLength =1000

print(id(body))

pprint(rocket.bodies)

print("------------------------------\n")

body = Body() # この瞬間に参照は終了するので, 新たに初期化しても元の配列は不変

print(id(body))

pprint(rocket.bodies)

print("------------------------------\n")

# リスト内包表記を使えば耐える
rocket = Rocket()
rocket.bodies = np.array([Body() for _ in range(2)])

print([id(body) for body in rocket.bodies]) # ちゃんと違う!!!

body : Body = rocket.bodies[0]
body.refLength =1000

print(id(body))

pprint(rocket.bodies)

print("------------------------------\n")
