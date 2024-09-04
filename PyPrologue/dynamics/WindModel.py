'''
風モデルクラス

大気モデルは国際標準大気参考にしている  
JP Wikipedia: https://ja.wikipedia.org/wiki/%E5%9B%BD%E9%9A%9B%E6%A8%99%E6%BA%96%E5%A4%A7%E6%B0%97  
EN Wikipedia: https://en.wikipedia.org/wiki/International_Standard_Atmosphere

実際に実装したモデル: https://pigeon-poppo.com/standard-atmosphere/  
上記サイトが参照しているNASAの論文: https://ntrs.nasa.gov/citations/19770009539
'''
import numpy as np
import pandas as pd
from PyPrologue.app.AppSetting import *
from PyPrologue.app.CommandLine import *
import PyPrologue.misc.Constant as Constant
from dataclasses import dataclass
from typing import Literal


@dataclass
class WindData:
    '''
    風データ構造体
    '''
    height : float = 0
    speed : float = 0
    direction : float = 0
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WindData): return NotImplemented
        return self.height == other.height and self.speed == other.speed and self.direction == other.direction

class WindModel :
    __windData = np.array([])
    __groundWindSpeed : float     = 0
    __groundWindDirection : float = 0
    __directionInterval : float   = 0
    __height : float              = 0
    __geopotentialHeight          = 0
    __airDensity : float          = 0
    __gravity : float             = 0
    __pressure : float            = 0
    __temperature : float         = 0
    __wind = np.array([])
    
   
    
    def __init__(self, 
                  magneticDeclination : float, groundwindSpeed : float = 0, groundWindDirection : float = 0):
        '''
        コンストラクタ.
        
        Args:
            magneticDeclination : 磁気偏角.
            groundwindSpeed     : 地上風速 (original または only_powerlawでのみ有効)
            groundWindDirection : 地上風向 (original または only_powerlawでのみ有効)
        '''
        if AppSetting.windModel.type == WindModelType.Real:
            df = pd.read_csv("input/wind/" + AppSetting.windModel.realdataFileName)
            df = df.sort_values(by=df.columns[0]) # sort by geopotential_height
            for idx, windData in df.iterrows():
                self.__windData = np.append(self.__windData, 
                    WindData(height=windData[0], speed=windData[1], direction=windData[2]-magneticDeclination)) # type: ignore
        else:
            self.__groundWindSpeed = groundwindSpeed
            self.__groundWindDirection = (groundWindDirection - magneticDeclination) % 360
            self.__directionInterval = 270 - self.__groundWindDirection if self.__directionInterval > 45.0 else 270 - self.__groundWindDirection + 360
        
        
    
    def update(self, height : float):
        '''
            高さを更新
            Args:
                height : 高度.
            Returns:
                None    
        '''
        self.__height = height
        # この順番で計算しないと値が上手く更新されないので注意
        self.__geopotentialHeight = self.__getGeopotentialHeight()
        self.__gravity = self.__getGravity()
        self.__temperature = self.__getTemperature()
        self.__pressure = self.__getPressure()
        self.__airDensity = self.__getAirDensity()
        
        match AppSetting.windModel.type:
            case WindModelType.Real:
                self.__wind = self.__getWindFromData()
            case WindModelType.Original:
                self.__wind = self.__getWindOriginalModel()
            case WindModelType.OnlyPowerLaw:
                self.__wind = self.__getWindOnlyPowerLaw()
            case _: # NoWind or exception
                m_wind = -np.array([0.0, 0.0, 0.0])

    @property
    def geopotentialHeight(self) -> float:
        return self.__geopotentialHeight
    
    def __getGeopotentialHeight(self):
        '''Geopotential Height:  
        https://ja.wikipedia.org/wiki/%E3%82%B8%E3%82%AA%E3%83%9D%E3%83%86%E3%83%B3%E3%82%B7%E3%83%A3%E3%83%AB  
        Formula from: https://pigeon-poppo.com/standard-atmosphere/#i-2'''
        return Constant.EarthRadius * self.__height / (Constant.EarthRadius + self.__height)
    
    @property
    def gravity(self) -> float:
        return self.gravity
    
    def __getGravity(self) -> float:
        '''Formula from: https://ja.wikipedia.org/wiki/%E5%9C%B0%E7%90%83%E3%81%AE%E9%87%8D%E5%8A%9B#%E9%AB%98%E5%BA%A6'''
        return Constant.G * (Constant.EarthRadius / (Constant.EarthRadius + self.__height))**2
    
    @property
    def wind(self):
        return self.__wind
        
    @property
    def temperature(self) -> float:
        return self.__temperature
    
    def __getTemperature(self) -> float:
        '''Formula from: https://pigeon-poppo.com/standard-atmosphere/#i-3'''
        geopotentialHeight = self.geopotentialHeight
        for thresold, layer in zip(_layerThresholds[1:], _layers):
            if (geopotentialHeight < thresold):
                return layer.baseTemperature + layer.lapseRate * geopotentialHeight
        
        raise ValueError(f"Current height is {self.__height} m. "
                + "Wind model is not defined above 32000 m.")
    
    @property
    def pressure(self):
        return self.__pressure
    
    def __getPressure(self)->float:
        '''Formula from: https://keisan.casio.jp/exec/system/1203469826  
        はじめに記載した参考文献はおそらく間違っている  
        https://pigeon-poppo.com/standard-atmosphere/#i-4'''
        geopotentialHeight = self.geopotentialHeight
        for thresold, layer in zip(_layerThresholds[1:], _layers):
            if (geopotentialHeight < thresold):
                k : float = layer.lapseRate * self.__height
                return layer.basePressure * pow(k / (self.temperature - Constant.AbsoluteZero - k), 5.257)
            
        raise ValueError(f"Current height is {self.__height} m. "
                + "Wind model is not defined above 32000 m.")
    
    @property
    def density(self) -> float:
        return self.__airDensity
    
    def __getAirDensity(self) -> float:
        return self.pressure / (self.temperature - Constant.AbsoluteZero) * Constant.GasConstant
    
    def __getWindFromData(self):
        idx = 0
        for data in self.__windData:
            if data.height < self.__height:
                idx = idx+1
            else: break
        if idx == 0:
            return np.array([0, 0, 0])
        if idx == len(self.__windData) : idx = idx-1
        windData1 = self.__windData[idx-1]
        windData2 = self.__windData[idx]
        
        windSpeed =\
            np.interp(self.__height, [windData1.height, windData2.height], [windData1.speed, windData2.speed])
        direction =\
            np.interp(self.__height, [windData1.height, windData2.height], [windData1.direction, windData2.direction])
        
        rad = np.radians(direction)
        
        return -np.array([np.sin(rad), np.cos(rad), 0]) * windSpeed
    
    def __getWindOriginalModel(self):
        if self.__height <= 0:
            rad = np.radians(self.__groundWindDirection)
            groundWind = -np.array([np.sin(rad), np.cos(rad), 0]) * self.__groundWindSpeed
            return groundWind
        
        elif self.__height < wind.surfaceLayerLimit: # 接地境界層
            deltaDirection = self.__height / wind.EkmanLayerLimit * self.__directionInterval
            rad = np.radians(self.__groundWindDirection + deltaDirection)
            __wind = -np.array([np.sin(rad), np.cos(rad), 0]) * self.__groundWindSpeed
            return _applyPowerLaw(height=self.__height, wind=__wind)
        
        elif self.__height < wind.EkmanLayerLimit:
            deltaDirection = self.__height / wind.EkmanLayerLimit * self.__directionInterval
            rad = np.radians(self.__groundWindDirection + deltaDirection)
            
            borderWindSpeed = _applyPowerLaw(self.__height, self.__groundWindSpeed)
            
            k = (self.__height - wind.surfaceLayerLimit) / (wind.surfaceLayerLimit + np.sqrt(2))
            u = wind.geostrophicWind * (1 - np.exp(-k) * np.cos(k))
            v = wind.geostrophicWind * (1 - np.exp(-k) * np.sin(k))
            
            descentRate = (wind.geostrophicWind - u) / wind.geostrophicWind
            
            return -np.array([np.sin(rad), np.cos(rad), 0]) * borderWindSpeed * descentRate\
                    -np.array([u * np.sin(rad), v * np.cos(rad), v]) 

        else:
            return -np.array([wind.geostrophicWind, 0, 0])
    
    def __getWindOnlyPowerLaw(self):
        rad = np.radians(self.__groundWindDirection)
        groundWind = -np.array([np.sin(rad), np.cos(rad), 0]) * self.__groundWindSpeed
        if self.__height <= 0:
            return groundWind
        else:
            return _applyPowerLaw(height=self.__height,wind=groundWind)
            
            
@dataclass
class __Layer :
    baseTemperature :float
    lapseRate : float
    basePressure : float
    baseDensity : float


# !! Geopotential altitude
# 0 ~ 11000 [m]    : Troposphere
# 11000 ~ 20000 [m]: Tropopause
# 20000 ~ 32000 [m]: Stratosphere
# 32000 ~ [m]      : Undefined and an error will occur if the altitude exceeds this
_layerThresholds = [0, 11000, 20000, 32000]

# 各層におけるパラメータ
_layers = [
    __Layer(
        baseTemperature=AppSetting.atmosphere.baseTemperature,
        lapseRate=-6.5e-3,
        basePressure=AppSetting.atmosphere.basePressure,
        baseDensity=1.2985),
    __Layer(baseTemperature=-56.5, lapseRate=0.0e-3, basePressure=22632.064, baseDensity=0.3639),
    __Layer(baseTemperature=-76.5, lapseRate=1.0e-3, basePressure=5474.889,  baseDensity=0.0880)]

@dataclass
class __Wind:
    geostrophicWind     = 15  # 地衡風 [m/s]
    surfaceLayerLimit   = 300  # 接地境界層 0 ~ 300 [m]
    EkmanLayerLimit     = 1000  # エクマン層 300 ~ 1000 [m]
wind : __Wind = __Wind()

def _applyPowerLaw(height: float, windSpeed: float | None = None, wind: np.ndarray | None = None,  ):
    multiplier = pow(height / AppSetting.windModel.powerLawBaseAlatitude, 1.0 / AppSetting.windModel.powerConstant)
    
    if   (windSpeed is not None and wind is not None):
        return (windSpeed * multiplier, wind * multiplier)
    elif (windSpeed is not None):
        return windSpeed * multiplier
    elif (wind is not None):
        return wind * multiplier
    else:
        return None
