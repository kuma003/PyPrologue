'''
dynamicsファイルデバッグ用コード
'''
#--------------------------------PyPrologueをインポートするための処理--------------------------------#
import sys; import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # モジュール検索パス追加
os.chdir(os.path.join(os.path.dirname(__file__), '..')) # カレントディレクトリ変更
#------------------------------------------------終了-----------------------------------------------#

from PyPrologue.dynamics.WindModel import *
from PyPrologue.app.AppSetting import *

import numpy as np
from numpy.linalg import norm
import matplotlib.pyplot as plt

from pprint import pprint

alts = np.linspace(0, 10000, 100)

fig, axes = plt.subplots(2, 2, figsize=(12, 8))
titles = ["real", "original", "only power law", "no wind"]
for x in range(len(axes)):
    for y in range(len(axes[0])):
        axes[x][y].set_title(titles[x * len(axes[0]) + y])

def calcWindSpeed(wind_model : WindModel, alt : float):
    wind_model.update(alt)
    return norm(wind_model.wind)

print("------------------------------\n")

AppSetting._windModel.type = WindModelType.Real
wind_model = WindModel(8.92, 3, 220)
pprint(wind_model.__dict__)
axes[0][0].plot(alts, [calcWindSpeed(wind_model, alt) for alt in alts])

print("------------------------------\n")

AppSetting._windModel.type = WindModelType.Original
wind_model = WindModel(8.92, 3, 220)
pprint(wind_model.__dict__)
axes[0][1].plot(alts, [calcWindSpeed(wind_model, alt) for alt in alts])

print("------------------------------\n")

AppSetting._windModel.type = WindModelType.OnlyPowerLaw
wind_model = WindModel(8.92, 3, 220)
axes[1][0].plot(alts, [calcWindSpeed(wind_model, alt) for alt in alts])
pprint(wind_model.__dict__)

print("------------------------------\n")

AppSetting._windModel.type = WindModelType.NoWind
wind_model = WindModel(8.92, 3, 220)
pprint(wind_model.__dict__)
axes[1][1].plot(alts, [calcWindSpeed(wind_model, alt) for alt in alts])

print("------------------------------\n")
plt.show()