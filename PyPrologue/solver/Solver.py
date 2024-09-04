'''
解析用クラス
'''
from PyPrologue.dynamics.WindModel import *
from PyPrologue.env.Environment import *
from PyPrologue.env.Map import *
from PyPrologue.result.SimuResult import *
from PyPrologue.rocket.Rocket import *
from PyPrologue.rocket.RocketSpec import *
from PyPrologue.app.AppSetting import *
from PyPrologue.app.CommandLine import *

from enum import Enum, auto

class TrajectoryMode(Enum):
    Trajectory = 1
    Parachute = auto()

class RocketType(Enum):
    Single = 1
    Multi = auto()

class DetachType(Enum):
    BurningFinished = 1
    Time = auto()
    SyncPara = auto()
    DoNotDetach = auto()

class Solver:
    _dt : float
    _environment : Environment
    _mapData : MapData
    _rocketType : RocketType
    _trajectoryMode : TrajectoryMode
    _detachType : DetachType
    _detachTime : float
    _rocketSpec : RocketSpecification
    
    # Simulation
    _rocket : Rocket
    _bodyDelta : Body
    _windModel : WindModel
    _currentBodyIndex : int = 0  # Index of the body being solved
    _detachCount : int = 0
    _steps : int = 0
    
    # Result
    _resultLogger : SimuResultLogger | None = None
    
    def __init__(self, 
                 mapData : MapData,
                 rocketType : RocketType,
                 mode : TrajectoryMode,
                 detachType : DetachType,
                 detachTime : float,
                 env : Environment,
                 spec : RocketSpecification) -> None:
        pass
    
    def _initializeRocket(self):
        pass
    
    def update(self):
        pass
    
    def updateParachute(self):
        pass
    
    def updateDetachment(self):
        pass
    
    def updateAerodynamicParameters(self):
        pass
    
    def updateRopcketProperties(self):
        pass