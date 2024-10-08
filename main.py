'''
プログラムの開始関数
'''

from PyPrologue.app.AppSetting import *
from PyPrologue.app.CommandLine import *
from PyPrologue.simulator.SimulatorFactory import *

VERSION = "0.1.0"

def main():
    print(f"Prologue v{VERSION}\n")
    
    # コマンドライン引数からの処理はとりあえず無し
    
    ShowSettingInfo()
    
    # SimulatorBaseインスタンスの生成
    # SimulatorBase抽象クラスの参照 (実際はid) を受け取っているが, 実際の中身はDetailSimulator型またはScatterSimulator型
    simulator = SimulatorFactory.Create()
    
    if simulator is None:
        PrintInfo(PrintInfoType.Error, "Failed to initialize simulator")
        return 1
    
    # シミュレーション実行
    try:
        if not simulator.run(True):
            raise RuntimeError("Failed to simulate.")
    except Exception as e:
        PrintInfo(PrintInfoType.Error, e)
        return 1    

def ShowSettingInfo():
    match AppSetting.windModel.type:
        case WindModelType.Real:
            windFile = f"Wind data file {AppSetting.windModel.realdataFileName}"
            PrintInfo(PrintInfoType.Information, "Wind model: Real", windFile, "Run detail mode simulation")
        case WindModelType.Original:
            PrintInfo(PrintInfoType.Information, "Wind model: Original")
        case WindModelType.OnlyPowerLaw:
            PrintInfo(PrintInfoType.Information, "Wind model; Only power law")
        case WindModelType.NoWind:
            PrintInfo(PrintInfoType.Information, "Wind model: No wind")


if __name__ == "__main__":
    main()
    