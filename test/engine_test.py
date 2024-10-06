'''
engine.pyデバッグ用コード
'''
#--------------------------------PyPrologueをインポートするための処理--------------------------------#
import sys; import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # モジュール検索パス追加
os.chdir(os.path.join(os.path.dirname(__file__), '..')) # カレントディレクトリ変更
#------------------------------------------------終了-----------------------------------------------#

from PyPrologue.rocket.Engine import *
import matplotlib.pyplot as plt

engine = Engine()
engine.loadThrustData( "I260_440cc_test0003_prologue.txt")
print(engine.thrustAt(0.0, 101325))
t = np.linspace(0, 3, 100)

thrust = [engine.thrustAt(time, 101325) for time in t]
plt.plot(t, thrust)
plt.show()
