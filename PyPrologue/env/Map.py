'''
マップクラス及び各マップ定義
'''
import json
from PyPrologue.env.GeoCoordinate import GeoCoordinate
from PyPrologue.utils.JsonUtils import GetValueExc
from enum import Enum

class MapType(Enum):
    NOSHIRO_SEA = 0
    NOSHIRO_LAND = 1
    IZU_SEA = 2
    IZU_LAND = 3
    UNKNOWN = 4

class MapData:
    key : str
    type : MapType
    coordinate : GeoCoordinate
    magneticDeclination : float
    
    def __init__(self,
        keyForJson : str, 
        mapType : MapType,
        magneticDeclination : float,
        launchPointLatitude : float,
        launchPointLongitude: float):
        self.key = keyForJson
        self.type = mapType
        self.coordinate = GeoCoordinate(launchPointLatitude, launchPointLongitude), # type: ignore
        self.magneticDeclination = magneticDeclination
    

__config_json_dict : dict = {}

def __InitValue(*keys : str):
    global __config_json_dict
    if __config_json_dict == {}:
        # JSONファイル読み込み.
        with open("input/map/config.json") as f:
            __config_json_dict = json.load(f)
    
    return GetValueExc(__config_json_dict, *keys)

NoshiroLand : MapData = MapData(
    keyForJson="noshiro_land",
    mapType=MapType.NOSHIRO_LAND,
    magneticDeclination=__InitValue("nosiro_land", "magnetic_declination"), # type: ignore
    launchPointLatitude=__InitValue("nosiro_land", "latitude"), # type: ignore
    launchPointLongitude=__InitValue("nosiro_land", "longitude") # type: ignore
)
NoshiroSea : MapData = MapData(
    keyForJson="nosiro_sea",
    mapType=MapType.NOSHIRO_LAND,
    magneticDeclination=__InitValue("nosiro_sea", "magnetic_declination"), # type: ignore
    launchPointLatitude=__InitValue("nosiro_sea", "latitude"), # type: ignore
    launchPointLongitude=__InitValue("nosiro_sea", "longitude") # type: ignore
)
IzuLand : MapData = MapData(
    keyForJson="izu_land",
    mapType=MapType.NOSHIRO_LAND,
    magneticDeclination=__InitValue("izu_land", "magnetic_declination"), # type: ignore
    launchPointLatitude=__InitValue("izu_land", "latitude"), # type: ignore
    launchPointLongitude=__InitValue("izu_land", "longitude") # type: ignore
)
IzuSea : MapData = MapData(
    keyForJson="izu_sea",
    mapType=MapType.NOSHIRO_LAND,
    magneticDeclination=__InitValue("izu_sea", "magnetic_declination"), # type: ignore
    launchPointLatitude=__InitValue("izu_sea", "latitude"), # type: ignore
    launchPointLongitude=__InitValue("izu_sea", "longitude") # type: ignore
)

def GetMap(key : str) -> MapData | None:
    global NoshiroLand, NoshiroSea, IzuLand, IzuSea
    match key:
        case "noshiro_land":
            return NoshiroLand
        case "noshiro_sea":
            return NoshiroSea
        case "izu_land":
            return IzuLand
        case "izu_sea":
            return IzuSea
        case _: # case default:
            return None

# MapTypeで受け付けるやつを作ったけど, こっちは不要だった...
# def GetMap(type : MapType) -> MapData | None:
#     global NoshiroLand, NoshiroSea, IzuLand, IzuSea
#     match type:
#         case MapType.NOSHIRO_LAND:
#             return NoshiroLand
#         case MapType.NOSHIRO_SEA:
#             return NoshiroSea
#         case MapType.IZU_LAND:
#             return IzuLand
#         case MapType.IZU_SEA:
#             return IzuSea
#         case _: # case default:
#             return None
