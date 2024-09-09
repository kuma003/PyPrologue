'''
シミュレータークラス
ファイル読み取り、初期化を行い結果を元にSolverクラスで解析を実行する
class SimulatorBaseは抽象クラスとして定義しているためそのままでは使えない
Detail/Scatterモードに対して、SimulatorBaseクラスを継承したDetailSimulator/ScatterSimulatorを定義している
抽象クラスでは、継承したクラスでその内部実装を変更することできる
デコレータ : @abstractmethodを付けた関数は継承先で必ず実装しなければならない
'''

from PyPrologue.app.AppSetting import *
from PyPrologue.app.CommandLine import *
from PyPrologue.env.Environment import *
from PyPrologue.env.Map import *
from PyPrologue.rocket.RocketSpec import *
from PyPrologue.result.ResultSaver import *
from PyPrologue.solver.Solver import *

import time
from pathlib import Path

from abc import ABC, abstractmethod # 抽象クラス
from enum import Enum, auto
from dataclasses import dataclass

class SimulationMode(Enum):
    Scatter : int = 1
    Detail : int = auto()

class SimulatorBase(ABC):
    @dataclass
    class SimulationSetting: 
        simulationMode : SimulationMode = SimulationMode.Scatter
        trajectoryMode : TrajectoryMode = TrajectoryMode.Trajectory
        detachType : DetachType = DetachType.BurningFinished
        detachTime : float    = 0.0
        windSpeed : float     = 0.0
        windDirection : float = 0.0
    
    def __init__(self, specName : str, specJson : dict, setting : SimulationSetting) -> None:
        # protected
        self._specName : str = specName
        self._setting : SimulatorBase.SimulationSetting = setting
        self._rocketType : RocketType = \
            RocketType.Multi if RocketSpecification.isMultipleRocket(specJson) else RocketType.Single
        self._rocketSpec     = RocketSpecification(specJson_dict=specJson)
        self._environment    = Environment(specJson=specJson)
        self._mapData        = self.__getMapData()
        self._outputdDirName = self.__getOutputDirectoryName()
    
    def run(self, output : bool) -> bool:
        self.__createResultDirectory()
        
        # Simulate
        start = time.time()
        
        if not self._simulate(): return False # faild
        
        elapsed_time = time.time() - start
        PrintInfo(PrintInfoType.Information,
                  f"Finish processing: {elapsed_time:.2f}[s]")
        
        # Save result and init commandline
        if output:
            PrintInfo(PrintInfoType.Information, "Saving result...")
            
            self._saveResult()
            
            PrintInfo(PrintInfoType.Information, f"Result is saved in \"{self._outputdDirName}\"")
        
        return True        
    
    @property
    def getOutputDirectory(self) -> str:
        return self._outputDirName
    
    @abstractmethod
    def simulate(self) -> bool:
        pass
    
    @abstractmethod
    def saveResult(self) -> None:
        pass
    
    def __createResultDirectory(self) -> None:
        output = Path(f"result/{self._outputdDirName}")
        output.mkdir(parents=True, exist_ok=True)
        if not output.is_dir():
            PrintInfo(PrintInfoType.Error, "Failed to create result directory")
    
    def __getOutputDirectoryName(self) -> str:
        dir = self._specName
        
        dir += "["
        
        match AppSetting.windModel.type:
            case WindModelType.Real:
                realWindFile = Path(AppSetting.windModel.realdataFileName)
                dir += f"({realWindFile.stem})"
            case WindModelType.Original:
                dir += "original"
            case WindModelType.OnlyPowerLaw:
                dir += "powerlaw"
            case WindModelType.NoWind:
                dir += "nowind"
            case _: # default:
                dir += "unknown"
        
        if not AppSetting.windModel.type == WindModelType.Real:
            match self._setting.simulationMode:
                case SimulationMode.Scatter:
                    dir += "_scatter"
                case SimulationMode.Detail:
                    dir += "_detail"
                case _: # default:
                    dir += "unknown"
        
        match self._setting.trajectoryMode:
            case TrajectoryMode.Parachute:
                dir += "_para"
            case TrajectoryMode.Trajectory:
                dir += "_traj"
            case _:
                dir += "unknown"
        
        dir += "]"
        
        if self._setting.simulationMode == SimulationMode.Detail and \
           AppSetting.windModel.type != WindModelType.Real and \
           AppSetting.windModel.type != WindModelType.NoWind:
            dir += f"[{self._setting.windSpeed:.2f}ms, {self._setting.windDirection:.2f}deg]"
        
        return dir
    
    def __getMapData(self) -> MapData:
        # Get / Set place
        place = self._environment.place.lower()
        map = GetMap(place)
        if map is None:
            return GetMap(place)
        else:
            raise RuntimeError("This map is invalid.")

class DetailSimulator(SimulatorBase):
    def __init__(self, specName: str, specJson: dict, setting: SimulatorBase.SimulationSetting) -> None:
        super().__init__(specName, specJson, setting)
        self._result = SimuResultSummary()
    
    def simulate(self) -> bool:
        try:
            solver = Solver(self._mapData, 
                            self._rocketType,
                            self._setting.trajectoryMode,
                            self._setting.detachType,
                            self._setting.detachTime,
                            self._environment,
                            self._rocketSpec)
            
            resultLogger = solver.solve(self._setting.windSpeed, self._setting.windDirection)
            resultLogger.organize()
            self._result = resultLogger.result
        except:
            return False # どっかでエラー吐いたらここでキャッチする
        return True
    
    def saveResult(self) -> None:
        dir : Path = Path(f"result/{self._outputdDirName}")
        ResultSaver.SaveDetail(dir, self._result)