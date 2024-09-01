'''
コマンド受付に関するインターフェース
'''

from enum import Enum

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

def InputIndex(size: int):
    var = -1
    while not(isinstance(var, int) and 0 < var <= size):
        input_str = input("")
        try:
            var = int(input_str)
        except ValueError or EOFError:
            var = -1

def PrintInfo(type : PrintInfoType, *lines : str):
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