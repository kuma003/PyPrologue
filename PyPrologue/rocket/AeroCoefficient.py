'''
対気速度に対する係数決定のためのクラス
'''
import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass

@dataclass
class AeroCoefSpec:
    airspeed : float = 0
    Cp : float   = 0
    Cp_a : float = 0
    Cd_i : float = 0
    Cd_f : float = 0
    Cd_a2: float = 0
    Cna : float  = 0

@dataclass
class AeroCoefficient:
    Cp : float  = 0
    Cd : float  = 0
    Cna : float = 0

class AeroCoefficientStrage:
    
    def __init__(self):
        self._aeroCoefSpec : np.ndarray[AeroCoefSpec] = np.array([], dtype=AeroCoefSpec)
        self._constant : AeroCoefficient = AeroCoefficient()
        self._isTimeSeries : bool = False
        
    
    @property
    def isTimeSeriesSpec(self): return self._isTimeSeries
    
    def init_by_JSON(self, Cp : float, Cp_a : float, Cd_i : float, Cd_f : float, Cd_a2 : float, Cna : float):
        self._aeroCoefSpec = np.array([AeroCoefSpec(
            airspeed=0, Cp=Cp, Cp_a=Cp_a, Cd_i=Cd_i, Cd_f=Cd_f, Cd_a2=Cd_a2, Cna=Cna
        )]) # type: ignore # 
    
    def setConstant(self, Cp : float, Cd : float, Cna : float):
        self._constant = AeroCoefficient(Cp=Cp, Cd=Cd, Cna=Cna)
    
    def init_by_CSV(self, filepath : Path):
        if not isinstance(filepath, Path): filepath = Path(filepath)
        if not filepath.exists() or filepath.suffix != ".csv":
            return
        
        df = pd.read_csv(filepath)
        if len(df.columns) < 7: return
        df = df.sort_values(by=df.columns[0]) # airspeedで昇順ソート
        self._aeroCoefSpec = df.apply(lambda row: AeroCoefSpec(row[0], row[1], row[2], row[3], row[4], row[5], row[6]), axis=1) # type: ignore
        
        self._isTimeSeries = True
    
    def valueIn(self, airspeed : float, attackAngle : float, CombustionEnded : bool) -> AeroCoefficient:
        spec : AeroCoefSpec
        
        if len(self._aeroCoefSpec) == 1:
            spec = self._aeroCoefSpec[0]
        else:
            if airspeed < self._aeroCoefSpec[0].airspeed:
                spec = self._aeroCoefSpec[0]
            elif airspeed > self._aeroCoefSpec[-1].airspeed:
                spec = self._aeroCoefSpec[-1]
            else:
                idx = 0
                for __spec in self._aeroCoefSpec:
                    if __spec.airspeed > airspeed:
                        idx = idx+1
                    else: break
                spec1 = self._aeroCoefSpec[idx-1]
                spec2 = self._aeroCoefSpec[idx]
                
                spec = AeroCoefSpec(
                    airspeed,
                    np.interp(airspeed, [spec1.airspeed, spec2.airspeed], [spec1.Cp, spec2.Cp]), # type: ignore
                    np.interp(airspeed, [spec1.airspeed, spec2.airspeed], [spec1.Cp_a, spec2.Cp_a]), # type: ignore
                    np.interp(airspeed, [spec1.airspeed, spec2.airspeed], [spec1.Cd_i, spec2.Cd_i]), # type: ignore
                    np.interp(airspeed, [spec1.airspeed, spec2.airspeed], [spec1.Cd_f, spec2.Cd_f]), # type: ignore
                    np.interp(airspeed, [spec1.airspeed, spec2.airspeed], [spec1.Cd_a2, spec2.Cd_a2]), # type: ignore
                    np.interp(airspeed, [spec1.airspeed, spec2.airspeed], [spec1.Cna, spec2.Cna]), # type: ignore
                )
        
        return AeroCoefficient(
            Cp=self._constant.Cp + spec.Cp + spec.Cp_a * attackAngle,
            Cd=self._constant.Cd + (spec.Cd_f if CombustionEnded else spec.Cd_i) + spec.Cd_a2 * attackAngle**2,
            Cna= self._constant.Cna + spec.Cna
        )