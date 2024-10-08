'''
シミュレーション結果に関するデータクラス
'''

from copy import deepcopy
from PyPrologue.dynamics.WindModel import *
from PyPrologue.env.Map import *
from PyPrologue.rocket.Rocket import *
from PyPrologue.rocket.RocketSpec import*
import numpy as np
from numpy.linalg import norm

from dataclasses import dataclass, field

@dataclass
class SimuResultStep:
    '''ステップ毎の結果'''
    # general
    gen_timeFromLaunch : float = 0
    gen_elapsedTime : float = 0
    
    # Boolean
    launchClear : bool = False
    combusting : bool = False
    parachuteOpened : bool = False
    
    # Air
    air_density : float = 0
    air_gravity : float = 0
    air_pressure : float = 0
    air_temperature : float = 0
    air_wind : np.ndarray = field(default_factory=lambda: np.ndarray([0,0,0]))
    
    # Body
    rocket_mass : float = 0
    rocket_cgLength : float = 0
    rocket_iyz : float = 0
    rocket_ix : float = 0
    rocket_attackAngle : float = 0
    rocket_pos : np.ndarray = field(default_factory=lambda: np.ndarray([0,0,0]))
    rocket_velocity : np.ndarray = field(default_factory=lambda: np.ndarray([0,0,0]))
    rocket_airspeed_b : np.ndarray = field(default_factory=lambda: np.ndarray([0,0,0]))
    rocket_force_b : np.ndarray = field(default_factory=lambda: np.ndarray([0,0,0]))
    Cnp : float = 0; Cny : float = 0
    Cmqp : float = 0; Cmqy : float = 0
    Cp : float = 0
    Cd : float = 0
    Cna : float = 0
    
    latitude : float = 0
    longitude : float = 0
    downrange : float = 0
    
    Fst : float = 0
    dynamicPressure : float = 0

@dataclass
class SimuResultBody:
    '''各body(rocket1, rocket2, rocket3, ...)でのSimuResultStepを格納'''
    steps : np.ndarray = field(default_factory=lambda: np.array([], dtype=SimuResultStep))

@dataclass
class BodyFinalPosition:
    '''bodyの最終落下地点'''
    latitude : float = 0
    longitude : float = 0

@dataclass
class SimuResultSummary:
    '''シミュレーション結果の主要な値を格納'''
    bodyResults : np.ndarray = field(default_factory=lambda: np.array([], dtype=SimuResultBody))
    bodyFinalPositions : np.ndarray = field(default_factory=lambda: np.array([], dtype=BodyFinalPosition))
    
    # condition
    windSpeed : float = 0
    windDirection : float = 0
    
    # launch clear
    launchClearTime : float = 0
    launchClearVelocity : np.ndarray = field(default_factory=lambda: np.ndarray([0,0,0]))
    
    # max
    maxAltitude : float = 0; detectPeakTime : float = 0
    maxVelocity : float = 0
    maxAirspeed : float = 0
    maxNormalForceDuringRising : float = 0

class SimuResultLogger:
    '''ステップごとに結果を格納、出力を行うクラス  
    元実装がshared_ptrなのですべて静的変数 (クラス変数) としている'''
    _rocketSpec :RocketSpecification
    _map : MapData
    _result : SimuResultSummary
    
    def __init__(self, rocketSpec : RocketSpecification, map : MapData, windSpeed : float, windDirection : float):
        # あくまでもクラス変数としてアクセス
        SimuResultLogger._rocketSpec = rocketSpec
        SimuResultLogger._map = map
        SimuResultLogger._result = SimuResultSummary()
        SimuResultLogger._result.windSpeed = windSpeed
        SimuResultLogger._result.windDirection = windDirection
    
    @property
    def result(self):
        return SimuResultLogger._result

    @property
    def resultScatterFormat(self):
        result : SimuResultSummary = self._result
        
        # remove steps that are not landing point
        for body in result.bodyResults:
            lastBody : SimuResultStep = body.steps[-1]
            body.steps = np.array([lastBody])
        
        # remove body result that not contain valid landing point
        return result.bodyResults[[body_result.steps[-1].rocket_pos[2]  <= 0 for body_result in result.bodyResults]]
    
    def pushBody(self):
        SimuResultLogger._result.bodyResults = np.append(SimuResultLogger._result.bodyResults, SimuResultBody())
        SimuResultLogger._result.bodyFinalPositions = np.append(SimuResultLogger._result.bodyFinalPositions, BodyFinalPosition())
    
    def setLaunchClear(self, body : Body):
        SimuResultLogger._result.launchClearTime    = body.elapsedTime
        SimuResultLogger._result.launchClearVelocity = deepcopy(body.velocity)
    
    def setBodyFinalPosition(self, bodyIndex : int, pos : np.ndarray):
        SimuResultLogger._result.bodyFinalPositions[bodyIndex] = BodyFinalPosition(latitude  = SimuResultLogger._map.coordinate.latitudeAt(pos[1]), 
                                                                       longitude = SimuResultLogger._map.coordinate.longitudeAt(pos[0]))
    
    def update(self, bodyIndex : int, rocket : Rocket, body : Body, windModel : WindModel, combusting : bool):
        spec = SimuResultLogger._rocketSpec.bodySpec(bodyIndex=bodyIndex)
        
        step = SimuResultStep(
            # General
            gen_elapsedTime=rocket.timeFromLaunch,
            gen_timeFromLaunch=body.elapsedTime,
            
            # Boolean
            launchClear=rocket.launchClear,
            combusting=combusting,
            parachuteOpened=body.parachuteOpened,
            
            # Air
            air_density=windModel.density,
            air_gravity=windModel.gravity,
            air_pressure=windModel.pressure,
            air_temperature=windModel.temperature,
            air_wind=windModel.wind,
            
            # body
            rocket_mass=body.mass,
            rocket_cgLength=body.refLength,
            rocket_iyz=body.iyz,
            rocket_ix=body.ix,
            rocket_attackAngle=body.attackAngle,
            rocket_pos=deepcopy(body.pos),
            rocket_velocity=deepcopy(body.velocity),
            rocket_airspeed_b=deepcopy(body.airspeed_b),
            rocket_force_b=deepcopy(body.force_b),
            Cnp=body.Cnp,
            Cny=body.Cny,
            Cmqp=body.Cmqp,
            Cmqy=body.Cmqy,
            Cp=body.aeroCoef.Cp,
            Cd=body.aeroCoef.Cd,
            Cna=body.aeroCoef.Cna,
            
            # position
            latitude=SimuResultLogger._map.coordinate.latitudeAt(body.pos[1]),
            longitude=SimuResultLogger._map.coordinate.longitudeAt(body.pos[0]),
            downrange=norm(body.pos[0:2]),
            
            # calculated
            Fst=100 * (body.aeroCoef.Cp - body.refLength) / spec.length,
            dynamicPressure=0.5 * windModel.density * norm(body.airspeed_b)**2
        )
        
        SimuResultLogger._result.bodyResults[bodyIndex].steps = np.append(SimuResultLogger._result.bodyResults[bodyIndex].steps, step)
        
        # update max
        rising : bool = body.velocity[2] > 0
        if SimuResultLogger._result.maxAltitude < body.pos[2]:
            SimuResultLogger._result.maxAltitude   = body.pos[2]
            SimuResultLogger._result.detectPeakTime = body.elapsedTime
        if SimuResultLogger._result.maxVelocity < norm(body.velocity):
            SimuResultLogger._result.maxVelocity = norm(body.velocity)
        if SimuResultLogger._result.maxAirspeed < norm(body.airspeed_b):
            SimuResultLogger._result.maxAirspeed = norm(body.airspeed_b)
        if rising and SimuResultLogger._result.maxNormalForceDuringRising < norm(body.force_b[1:]):
            SimuResultLogger._result.maxNormalForceDuringRising = norm(body.force_b[1:])
    
    
    def organize(self):
        for bodyResult in SimuResultLogger._result.bodyResults:
            for step in bodyResult.steps:
                if step.rocket_pos[2] < 0:
                    step.rocket_pos[2] = 0.0
    