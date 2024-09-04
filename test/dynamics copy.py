'''
dynamicsファイルデバッグ用コード
'''
#--------------------------------PyPrologueをインポートするための処理--------------------------------#
import sys; import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # モジュール検索パス追加
os.chdir(os.path.join(os.path.dirname(__file__), '..')) # カレントディレクトリ変更
#------------------------------------------------終了-----------------------------------------------#

from PyPrologue.dynamics.WindModel import *

from pprint import pprint

print("------------------------------\n")
