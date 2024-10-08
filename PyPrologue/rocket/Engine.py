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
    time : np.ndarray[float] = np.array([])
    thrust : np.ndarray[float] = np.array([])

class Engine:   
    def __init__(self):
        self.__thrustData : ThrustData = ThrustData()
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
        
        self.__thrustData = ThrustData(df.iloc[:, 0].to_numpy(), df.iloc[:, 1].to_numpy())
                
        self.__exist = True
        return True        
    
    def thrustAt(self, time : float, pressure : float):
        thrust = np.interp(time, self.__thrustData.time, self.__thrustData.thrust, left=0.0, right=0.0) # 外挿はせずに0. 内部はcだから早いはず...
        
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
        return self.__thrustData.time[-1] if self.__exist else 0.0
    
    def isCombusting(self, time : float) -> bool:
        return time < self.combustionTime if self.__exist else False
    
    def didCombustion(self, time : float) -> bool:
        return time > self.combustionTime if self.__exist else True