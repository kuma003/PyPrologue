'''
ロケットの緒元に関するデータクラス
'''
import numpy as np
from PyPrologue.app.CommandLine import *
from PyPrologue.rocket.AeroCoefficient import *
from PyPrologue.rocket.Engine import *
from PyPrologue.utils.JsonUtils import *
import PyPrologue.misc.Constant as Constant
from enum import Enum
from dataclasses import dataclass, field

class ParachuteOpeningType(Enum):
    DetectPeak = 0
    FixedTime = 1
    TimeFromDetectPeak = 2

@dataclass
class Parachute:
    openingType : ParachuteOpeningType = ParachuteOpeningType.DetectPeak
    terminalVelocity : float = 0
    openingTime : float = 0
    openingHeight : float = 0
    
    Cd : float = 0

@dataclass
class Transition:
    time : float = 0
    mass : float = 0
    Cd : float = 0

@dataclass
class BodySpecification:
    length : float = 0
    diameter : float = 0
    bottomArea : float = 0
    
    CGLengthInitial : float = 0
    CGLengthFinal : float = 0
    
    massInitial : float = 0
    massFinal : float = 0
    
    rollingMomentInertiaInitial : float = 0
    rollingMomentInertiaFinal : float = 0
    
    Cmq : float = 0
    
    parachutes : np.ndarray = field(default_factory=lambda: np.array([], dtype=Parachute))
    
    engine : Engine = field(default_factory=Engine)
    aeroCoeffStorage : AeroCoefficientStrage = field(default_factory=AeroCoefficientStrage)
    
    transitions : np.ndarray = field(default_factory=lambda: np.array([], dtype=Transition))

class RocketSpecification:
    _bodySpecs : np.ndarray
    _existInfCd : bool
    
    def __init__(self, specJson_dict : dict) -> None:
        self._existInfCd = False
        self._bodySpecs = np.array([])
        
        isMultipleRocket : bool = self.isMultipleRocket(specJson_dict)
        self.__setBodySpecification(specJson_dict=specJson_dict, index=0) # 第一段階目
        idx : int = 1
        while isMultipleRocket and idx < _availableBodyCount:
            self.__setBodySpecification(specJson_dict=specJson_dict, index=idx)
            idx = idx + 1
        
        # Set parachute Cd (Multiple rocket)
        if self._existInfCd:
            self.__setInfParachuteCd()        
        
        return

    def isMultipleRocket(self, specJson_dict : dict):
        return _bodyList[1] in specJson_dict    
    
    @property
    def bodyCount(self) -> int:
        return len(self._bodySpecs)
    
    def bodySpec(self, bodyIndex : int):
        return self._bodySpecs[bodyIndex] if 0 < bodyIndex < self.bodyCount else None
    
    def __setBodySpecification(self, specJson_dict : dict, index : float) -> None:
        key : str = _bodyList[index]
                
        spec = BodySpecification()
        
        spec.length =  GetValueExc(specJson_dict, key, "ref_len")
        spec.diameter = GetValueExc(specJson_dict, key, "diam")
        spec.bottomArea = spec.diameter**2 / 4 * np.pi
        
        spec.CGLengthFinal = GetValueExc(specJson_dict, key, "CGlen_f")
        spec.CGLengthInitial = GetValueExc(specJson_dict, key, "CGlen_i")

        spec.massInitial = GetValueExc(specJson_dict, key, "mass_i")
        spec.massFinal = GetValueExc(specJson_dict, key, "mass_f")
        
        spec.rollingMomentInertiaInitial = GetValueExc(specJson_dict, key, "Iyz_i")
        spec.rollingMomentInertiaFinal = GetValueExc(specJson_dict, key, "Iyz_f")
        
        spec.Cmq = GetValueExc(specJson_dict, key, "Cmq")
        
        spec.parachutes = np.array([
            Parachute(
                openingType=ParachuteOpeningType(GetValue(specJson_dict, key, "op_type_1st")),
                terminalVelocity=GetValue(specJson_dict, key, "vel_1st"),
                openingTime=GetValue(specJson_dict, key, "op_time_1st"),
                openingHeight=GetValue(specJson_dict, key, "delay_time_1st")
        )])
        if spec.parachutes[0].terminalVelocity <= 0:
            self._existInfCd = True
            PrintInfo(PrintInfoType.Warning, 
                f"Rocket:{key}",
                "Terminal velocity is undefined.",
                "Parachute Cd value is automatically calculated.")
        else:
            spec.parachutes[0].Cd = _calcPrachuteCd(spec.massFinal, spec.parachutes[0].terminalVelocity)
        
        # initialize Engine
        spec.engine.loadThrustData(GetValue(specJson_dict, key, "motor_file", default_value=""))
        if "thrust_measured_pressure" in specJson_dict[key]:
            spec.engine.thrustMeasuredPressure = specJson_dict[key]["thrust_measured_pressure"]
        if "engine_nozzle_diameter" in specJson_dict[key]:
            spec.engine.nozzleDiameter = specJson_dict[key]["engine_nozzle_diameter"]
        
        spec.aeroCoeffStorage.init_by_CSV(GetValue(specJson_dict, key, "aero_coef_file", default_value=""))
        if spec.aeroCoeffStorage.isTimeSeriesSpec:
            PrintInfo(PrintInfoType.Information, f"Rocket: {key}", "Aero coefficients are set from CSV")
        else:
            PrintInfo(PrintInfoType.Information, f"Rocket: {key}", "Aero coefficients are set from JSON")
            spec.aeroCoeffStorage.init_by_JSON(GetValueExc(specJson_dict, key, "CPlen"),
                                               GetValue(specJson_dict, key, "CP_alpha"),
                                               GetValueExc(specJson_dict, key, "Cd_i"),
                                               GetValueExc(specJson_dict, key, "Cd_f"),
                                               GetValue(specJson_dict, key, "Cd_alpha2"),
                                               GetValueExc(specJson_dict, key, "Cna"))
        self._bodySpecs = np.append(self._bodySpecs, spec)
        
        try:
            for child in specJson_dict[key]["transitions"]:
                spec.transitions = np.append(spec.transitions, Transition(time=GetValueExc(child, "time"),
                                                                                     mass=GetValueExc(child, "mass"),
                                                                                     Cd=GetValueExc(child, "Cd")))
        except:
            pass # 空実装
        
        self.bodySpec = np.append(self.bodySpec, spec)
    
    def __setInfParachuteCd(self):
        # memo: 
        #  Pythoではミュータブルオブジェクト(変更可能)ならfor文は参照渡しとして機能する
        for spec in self._bodySpecs:
            if spec.parachutes[0].Cd == 0:
                for _spec in reversed(self._bodySpecs):
                    spec.parachutes[0].Cd = spec.parachutes[0].Cd + _spec.parachutes[0].Cd    

def _calcPrachuteCd(massFinal : float, termianlVelocity : float):
    return massFinal * Constant.G / (0.5 * 1.25 * termianlVelocity ** 2)

_bodyList = ["rocket1", "rocket2", "rocket3"]
_availableBodyCount = len(_bodyList)