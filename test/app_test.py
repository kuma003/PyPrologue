'''
appファイルデバッグ用コード
'''
#--------------------------------PyPrologueをインポートするための処理--------------------------------#
import sys; import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # モジュール検索パス追加
os.chdir(os.path.join(os.path.dirname(__file__), '..')) # カレントディレクトリ変更
#------------------------------------------------終了-----------------------------------------------#

from PyPrologue.app.CommandLine import *
from PyPrologue.app.AppSetting import *

from pprint import pprint
import time

QUESTION = False  # omit
APP_SETTIGN = False

if QUESTION: 
    print("------------------------------\n")

    PrintInfo(PrintInfoType.Information, "following is a", "question test.")
    Question("choose fruit", "apple", "banana", "others")
    InputIndex(2)

if APP_SETTIGN:
    print("------------------------------\n")

    pprint(AppSetting.__dict__)

for idx in progress_bar(100):
    time.sleep(0.01)