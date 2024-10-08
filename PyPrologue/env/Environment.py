'''
緒元JSONファイルenvironmentキーのインターフェース
'''
from dataclasses import dataclass
from PyPrologue.utils.JsonUtils import GetValueExc

@dataclass
class Environment:
    place : str
    railLength : float
    railAzimuth : float
    railElevation : float
    
    def __init__(self, specJson : dict):
        self.place         = GetValueExc(specJson, "environment", "place") # type: ignore
        self.railLength    = GetValueExc(specJson, "environment", "rail_len") # type: ignore
        self.railAzimuth   = GetValueExc(specJson, "environment", "rail_azi") # type: ignore
        self.railElevation = GetValueExc(specJson, "environment", "rail_elev") # type: ignore