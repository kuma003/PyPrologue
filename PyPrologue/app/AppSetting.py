'''
prologue.settings.json のインターフェース
'''
import json  # JSONファイル読み込み
from pathlib import Path
from enum import Enum  # 列挙体宣言用
from dataclasses import dataclass
from PyPrologue.app.CommandLine import *
from PyPrologue.utils.JsonUtils import GetValueExc

class WindModelType(Enum):
    Real = 1
    Original = 2
    OnlyPowerLaw = 3
    NoWind = 4

class _AppSetting:
    '''
    初期設定クラス. Prologueとはことなり Singleton にした.
    '''
    @dataclass
    class Processing:
        multiThread : bool
        threadCount : int
    _processing : Processing
    
    @property
    def processing(self)  -> Processing: return self._processing
    
    @dataclass
    class Simulation:
        dt : float
        detectPeakThreshold : float
        # scatter
        windSpeedMin : float
        windSpeedMax : float
        windDirInterval : float
    _simulation : Simulation
    
    @property
    def simulation(self)  -> Simulation: return self._simulation
    
    @dataclass
    class Result:
        precision : int
        stepSaveInterval : int
    _result : Result
    
    @property
    def result(self)  -> Result: return self._result

    @dataclass
    class WindModel:
        powerConstant : float
        powerLawBaseAlatitude : float
        type : WindModelType
        realdataFileName : str
    _windModel : WindModel
    
    @property
    def windModel(self)  -> WindModel: return self._windModel
    
    @dataclass
    class Atmoshere:
        basePressure : float
        baseTemperature : float
    _atmosphere : Atmoshere
    
    @property
    def atmosphere(self) : return self._atmosphere
    
    _json_dict : dict = {}
        
    def __new__(cls, *args, **kargs):
        if hasattr(cls, "_instance"): return cls._instance # すでにインスタンスがある場合.
        
        cls._instance = super(_AppSetting, cls).__new__(cls)
        self = cls._instance
        
        ### ここは一度だけ実行される ###
        
        self._processing = _AppSetting.Processing(
            multiThread=self.__InitValue("processing", "multi_thread"), # type: ignore
            threadCount=self.__InitValue("processing", "multi_thread_count") # type: ignore
        )            
        if self._processing.threadCount < 1:
            PrintInfo(PrintInfoType.Warning,
                "Specified thread count is too low",
                "Thread count is automatically set to 1.")
        # PythonのThreadingに上限はないので割愛
        
        self._simulation = _AppSetting.Simulation(
                dt                  = self.__InitValue("simulation", "dt"), # type: ignore
                detectPeakThreshold = self.__InitValue("simulation", "detect_peak_threshold"), # type: ignore
                windSpeedMin        = self.__InitValue("simulation", "scatter", "wind_speed_min"), # type: ignore
                windSpeedMax        = self.__InitValue("simulation", "scatter", "wind_speed_max"), # type: ignore
                windDirInterval     = self.__InitValue("simulation", "scatter", "wind_dir_interval") # type: ignore
                )
        
        self._result = _AppSetting.Result(
            precision       = self.__InitValue("result", "precision"), # type: ignore
            stepSaveInterval= self.__InitValue("result", "step_save_interval") # type: ignore
        )
        if self._result.precision < 0:
            PrintInfo(PrintInfoType.Warning, "Result precision is set to the default value of 8.")
            self._result.precision = 8
        if self._result.stepSaveInterval < 1:
            PrintInfo(PrintInfoType.Warning, "Step save interval is set to the default value of 10.")
            self._result.stepSaveInterval = 10
        
        self._windModel = _AppSetting.WindModel(
            powerConstant           = self.__InitValue("wind_model", "power_constant"), # type: ignore
            powerLawBaseAlatitude   = self.__InitValue("wind_model", "power_low_base_alt"), # type: ignore
            type                    = WindModelType.Original, # 仮に
            realdataFileName        = self.__InitValue("wind_model", "realdata_filename") # type: ignore
        )
        match self.__InitValue("wind_model", "type"):
            case "real":
                self._windModel.type = WindModelType.Real
            case "original":
                self._windModel.type = WindModelType.Original
            case "only_powerlaw":
                self._windModel.type = WindModelType.OnlyPowerLaw
            case "no_wind":
                self._windModel.type = WindModelType.Real
            case _: # default
                PrintInfo(PrintInfoType.Warning,
                    "In prologue.settings.json",
                    "wind_model.type",
                    "\"" + str(self.__InitValue("wind_model", "type")) + "\" is invalid string.",
                    "Set \"real\", \"original\", \"only_powerlow\" or \"no_wind\"",
                    "wind_model type is set to the default value of original.")
        if self._windModel.type == WindModelType.Real and not Path("input/wind/" + self._windModel.realdataFileName).exists():
            PrintInfo(PrintInfoType.Error,
                    "wind_model realdataFileName : " + str(Path("input/wind/" + self._windModel.realdataFileName))  +" does not exit.")
            raise FileExistsError
        
        self._atmosphere = _AppSetting.Atmoshere(
            basePressure    = self.__InitValue("atmosphere", "base_pressure_pascal"), # type: ignore
            baseTemperature = self.__InitValue("atmosphere", "base_temperature_celsius") # type: ignore
        )
        
        return cls._instance
    
    def __InitValue(self, *keys : str):
        if self._json_dict == {}:
            # JSONファイル読み込み.
            with open("prologue.settings.json") as f:
                json_dict : dict = json.load(f)
        
        return GetValueExc(json_dict, *keys)

AppSetting = _AppSetting()
