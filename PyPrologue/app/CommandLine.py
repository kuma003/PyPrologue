'''
コマンド受付に関するインターフェース
'''

from enum import Enum
import time

class PrintInfoType(Enum):
    Information = 1; Warning = 2; Error = 3

def Question(question : str, *choices : str) -> None:
    '''選択肢提示関数.
    Args:
        question: 疑問文.
        choices : 選択肢.
    '''
    print("<!==", question, "===!>")
    for choice, i in zip(choices, range(len(choices))):
        print(i+1, ": ", choice, sep="")

def InputIndex(size: int) -> int:
    '''インデックス入力関数.
    Args:
        size: 入力できる数の上限 (下限は0).
    '''
    var = -1
    while not(isinstance(var, int) and 0 < var <= size):
        input_str = input("")
        try:
            var = int(input_str)
        except ValueError or EOFError:
            var = -1
    print("")
    return var

def InputFloat(prompt : str) -> float:
    print(prompt)
    var = -1
    while not(isinstance(var, float)):
        input_str = input("")
        try:
            var = float(input_str)
        except ValueError or EOFError:
            var = -1
    print("")
    return var

def PrintInfo(type : PrintInfoType, *lines : str):
    '''文字列出力関数.
    Args:
        type: 情報のタイプ.
        line: 出力する文字. それぞれ改行して出力される.
    '''
    # 最初の文字を出力
    match(type):
        case PrintInfoType.Information:
            print("I: ", end="", sep="")
        case PrintInfoType.Warning:
            print("W: ", end="", sep="")
        case PrintInfoType.Error:
            print("E: ", end="", sep="")
        case _: # case default:
            print("I: ", end="", sep="")
    # テキストを出力
    for line, idx in zip(lines, range(len(lines))):
        if idx == 0:
            print(line, sep="")
        else:            
            print("   ", line, sep="")
    print("")

def progress_bar(epoch):
    # This code is a Python port version of progress_display class in boost progress.hpp.
    # Alhough original code was used as a only reference to develop this function,
    # license term is attached just in case.
    #
    # Copyright Beman Dawes 1994-99.  Distributed under the Boost
    # Software License, Version 1.0. (See accompanying file
    # LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
    #
    range(0)
    # 進捗度を表すバーを出力 
    print("0%   10   20   30   40   50   60   70   80   90   100") 
    print("|----|----|----|----|----|----|----|----|----|----|")
    steps = 51 # *の数. 
    start = time.time()
    for idx in range(epoch):
        progress = (idx + 1) / epoch
        bar = "*" * int(progress * steps) + " " * (steps - int(progress * steps))
        elapsed_time = time.time() - start
        est = 0 if progress == 0 else elapsed_time / progress - elapsed_time
        print(f"\r{bar}     {idx + 1}/{epoch}, Est:{est:.2f} s.", end="")
        yield idx
    print("")