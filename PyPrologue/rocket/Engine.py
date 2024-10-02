'''
エンジンクラス
'''
import numpy as np
import pandas as pd
from pathlib import Path
import PyPrologue.misc.Constant as Constant
from dataclasses import dataclass

@dataclass
class ThrustData:
    time : float = 0.0
    thrust : float = 0.0

class Engine:   
    def __init__(self):
        self.__thrustData : np.ndarray[ThrustData] = np.array([], dtype=ThrustData)
        self.__thrustMeasurePressure = 101325  # [Pa]
        self.__nozzleArea = 0.0  # [m^2]
        
        self.__exist : bool = False
    
    def loadThrustData(self, filepath : Path):
        if not isinstance(filepath, Path): filepath = Path(filepath)
        filepath = "input/thrust"/filepath
        if not filepath.is_file(): return False
        print(filepath)
        
        df = pd.read_csv(filepath, header=None, sep=None, engine="python")
        df = df.sort_values(df.columns[0])
        
        self.__thrustData = np.array(df.apply(lambda row : ThrustData(row[0], row[1]), axis=1)) # ndarray型にキャスト
                
        if self.__thrustData[0].time != 0:
            self.__thrustData = np.insert(self.__thrustData, 0, ThrustData(0, 0))
        
        self.__exist = True
        return True        
    
    def thrustAt(self, time : float, pressure : float):
        if not self.isCombusting(time): return 0
        
        idx = 0
        for data in self.__thrustData:
            if data.time < time:
                idx = idx+1
            else: break
        
        time1 = self.__thrustData[idx-1].time
        time2 = self.__thrustData[idx].time
        thrust1 = self.__thrustData[idx-1].thrust
        thrust2 = self.__thrustData[idx].thrust
        
        thrust = np.interp(time, [time1, time2], [thrust1, thrust2])
        
        return thrust + (self.thrustMeasuredPressure - pressure) * self.__nozzleArea
    
    @property
    def thrustMeasuredPressure(self): return self.__thrustMeasurePressure
    
    @thrustMeasuredPressure.setter
    def thrustMeasuredPressure(self, pressure) -> None: self.__thrustMeasurePressure = pressure
    
    @property
    def nozzleDiameter(self): return 2 * np.sqrt(self.__nozzleArea / np.pi)
    
    @nozzleDiameter.setter
    def nozzleDiameter(self, diameter) -> None: self.__nozzleArea = np.pi * (diameter ** 2) / 4
    
    @property
    def combustionTime(self) -> float:
        '''燃焼時間'''
        return self.__thrustData[-1].time if self.__exist else 0.0
    
    def isCombusting(self, time : float) -> bool:
        return time < self.combustionTime if self.__exist else False
    
    def didCombustion(self, time : float) -> bool:
        return time > self.combustionTime if self.__exist else True