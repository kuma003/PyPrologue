'''
緯度経度に関するクラス
'''
import PyPrologue.misc.Constant as Constant
import numpy as np

class GeoCoordinate:
    '''
    緯度経度に関するクラス
    '''
    __latitude : float   # launchpoint [deg N]
    __longitude : float  # launchpoint [deg E]
    __degPerLen_latitude : float
    __degPerLen_longitude : float
    
    def __init__(self, latitude : float, longitude : float):
        self.__latitude = latitude; self.__longitude = longitude
        
        self.__degPerLen_latitude  = 31.0 / 0.00027778
        self.__degPerLen_longitude = np.degrees(6378150.0 * np.cos(np.radians(latitude)))
    
    @property
    def latitude(self) -> float:
        return self.__latitude
    
    @property
    def longitude(self) -> float:
        return self.__longitude

    def latitudeAt(self, length) -> float:
        '''
        緯度を計算.
        Args:
            length : 緯度 (南北) 方向の移動距離
        '''
        return self.__latitude + length / self.__degPerLen_latitude
    
    def longitudeAt(self, length) -> float:
        '''
        経度を計算.
        Args:
            length : 経度 (東西) 方向の移動距離
        '''
        return self.__longitude + length / self.__degPerLen_longitude
    
    
        