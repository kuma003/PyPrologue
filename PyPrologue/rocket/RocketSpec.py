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
    __bodySpecs : np.ndarray
    __existInfCd : bool
    
    def RocketSpecification(self, specJson_dict : dict) -> None:
        self.__existInfCd = False
        
        isMultipleRocket : bool = self.isMultipleRocket(specJson_dict)
        self.__setBodySpecification(specJson_dict=specJson_dict, index=0) # 第一段階目
        idx : int = 1
        while isMultipleRocket and idx < __availableBodyCount:
            self.__setBodySpecification(specJson_dict=specJson_dict, index=idx)
            idx = idx + 1
        
        # Set parachute Cd (Multiple rocket)
        if self.__existInfCd:
            self.__setInfParachuteCd()        
        
        return

    def isMultipleRocket(self, specJson_dict : dict):
        return __bodyList[1] in specJson_dict    
    
    @property
    def bodyCount(self) -> int:
        return len(self.__bodySpecs)
    
    def bodySpec(self, bodyIndex : int):
        return self.__bodySpecs[bodyIndex] if 0 < bodyIndex < self.bodyCount else None
    
    def __setBodySpecification(self, specJson_dict : dict, index : float) -> None:
        key : str = __bodyList[index]
                
        spec = BodySpecification()
        
        spec.length =  GetValue(specJson_dict, "key", "ref_len")
        spec.diameter = GetValue(specJson_dict, key, "diam")
        spec.bottomArea = spec.diameter**2 / 4 * np.pi
        
        spec.CGLengthFinal = GetValue(specJson_dict, key, "CGlen_f")
        spec.CGLengthInitial = GetValue(specJson_dict, key, "CGlen_i")

        spec.massInitial = GetValue(specJson_dict, key, "mass_i")
        spec.massFinal = GetValue(specJson_dict, key, "mass_f")
        
        spec.rollingMomentInertiaInitial = GetValue(specJson_dict, key, "Iyz_i")
        spec.rollingMomentInertiaFinal = GetValue(specJson_dict, key, "Iyz_f")
        
        spec.Cmq = GetValue(specJson_dict, key, "Cmq")
        
        spec.parachutes = np.array([
            Parachute(
                openingType=ParachuteOpeningType(GetValue(specJson_dict, "key", "op_type_1st")),
                terminalVelocity=GetValue(specJson_dict, "key", "vel_1st"),
                openingTime=GetValue(specJson_dict, "key", "op_time_1st"),
                openingHeight=GetValue(specJson_dict, "key", "delay_time_1st")
        )])
        if spec.parachutes[0].terminalVelocity <= 0:
            self.__existInfCd = True
            PrintInfo(PrintInfoType.Warning, 
                f"Rocket:{key}",
                "Terminal velocity is undefined.",
                "Parachute Cd value is automatically calculated.")
        else:
            spec.parachutes[0].Cd = __calcPrachuteCd(spec.massFinal, spec.parachutes[0].terminalVelocity)
        
        # initialize Engine
        spec.engine.loadThrustData(GetValue(specJson_dict, key, "moter_file"))
        if "thrust_measured_pressure" in specJson_dict[key]:
            spec.engine.thrustMeasuredPressure = specJson_dict[key]["thrust_measured_pressure"]
        if "engine_nozzle_diameter" in specJson_dict[key]:
            spec.engine.nozzleDiameter = specJson_dict[key]["engine_nozzle_diameter"]
        
        spec.aeroCoeffStorage.init_by_CSV(GetValue(specJson_dict, key, "aero_coef_file"))
        if spec.aeroCoeffStorage.isTimeSeriesSpec:
            PrintInfo(PrintInfoType.Information, f"Rocket: {key}", "Aero coefficients are set from CSV")
        else:
            PrintInfo(PrintInfoType.Information, f"Rocket: {key}", "Aero coefficients are set from JSON")
            spec.aeroCoeffStorage.init_by_JSON(GetValue(specJson_dict, key, "CPlen"),
                                               GetValue(specJson_dict, key, "CP_alpha"),
                                               GetValue(specJson_dict, key, "Cd_i"),
                                               GetValue(specJson_dict, key, "Cd_f"),
                                               GetValue(specJson_dict, key, "Cd_alpha2"),
                                               GetValue(specJson_dict, key, "Cna"))
        self.__bodySpecs = np.append(self.__bodySpecs, spec)
        
        try:
            for child in specJson_dict[key]["transitions"]:
                spec.transitions = np.append(spec.transitions, Transition(time=GetValue(child, "time"),
                                                                                     mass=GetValue(child, "mass"),
                                                                                     Cd=GetValue(child, "Cd")))
        except:
            pass # 空実装
        
        self.bodySpec = np.append(self.bodySpec, spec)
    
    def __setInfParachuteCd(self):
        # memo: 
        #  Pythoではミュータブルオブジェクト(変更可能)ならfor文は参照渡しとして機能する
        for spec in self.__bodySpecs:
            if spec.parachutes[0].Cd == 0:
                for _spec in reversed(self.bodySpec):
                    spec.parachutes[0].Cd = spec.parachutes[0].Cd + _spec.parachutes[0].Cd    

def __calcPrachuteCd(massFinal : float, termianlVelocity : float):
    return massFinal * Constant.G / (0.5 * 1.25 * termianlVelocity ** 2)

__bodyList = ["rocket1", "rocket2", "rocket3"]
__availableBodyCount = len(__bodyList)