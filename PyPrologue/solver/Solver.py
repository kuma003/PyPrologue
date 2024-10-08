'''
解析用クラス
'''
from PyPrologue.dynamics.WindModel import *
from PyPrologue.env.Environment import *
from PyPrologue.env.Map import *
from PyPrologue.result.SimuResult import *
from PyPrologue.result.SimuResult import SimuResultLogger
from PyPrologue.rocket.Rocket import *
from PyPrologue.rocket.RocketSpec import *
from PyPrologue.app.AppSetting import *
from PyPrologue.app.CommandLine import *

import numpy as np
from numpy.linalg import norm
import quaternion
from copy import deepcopy

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
    def __init__(self, 
                 mapData : MapData,
                 rocketType : RocketType,
                 mode : TrajectoryMode,
                 detachType : DetachType,
                 detachTime : float,
                 env : Environment,
                 spec : RocketSpecification) -> None:
        self._dt : float                        = AppSetting.simulation.dt
        self._environment : Environment         = env
        self._mapData : MapData                 = mapData
        self._rocketType : RocketType           = rocketType
        self._trajectoryMode : TrajectoryMode   = mode
        self._detachType : DetachType           = detachType
        self._detachTime : float                = detachTime
        self._rocketSpec : RocketSpecification  = spec
        
        # Simulation
        self._rocket : Rocket       = Rocket()        
        self._bodyDelta : Body      = Body()
        self._windModel : WindModel = WindModel()
        self._currentBodyIndex : int= 0
        self._detachCount : int     = 0
        self._steps : int           = 0
        
        # Result
        self._resultLogger : SimuResultLogger | None = None
        
        self._rocket.bodies = np.array([Body() for _ in range(self._rocketSpec.bodyCount)])
    
    def solve(self, windSpeed : float, windDirection : float) -> SimuResultLogger:
        # initialize wind model
        match AppSetting.windModel.type:
            case WindModelType.Real:
                self._windModel = WindModel(magneticDeclination=self._mapData.magneticDeclination)
            case _: # case default
                self._windModel = WindModel(magneticDeclination=self._mapData.magneticDeclination, groundwindSpeed=windSpeed, groundWindDirection=windDirection)
        
        # may not failed to create WindModel...
        
        # Initialize result
        self._resultLogger = SimuResultLogger(self._rocketSpec, self._mapData, windSpeed, windDirection)
        self._resultLogger.pushBody()
        
        # Loop until all rockets are solved
        # Single rocket: solve once
        # Multi rokcet : every rockets including after detachment
        for solvedBodyCount in range(2 * self._detachCount + 1):
            self._steps = 0
            
            self._initializeRocket()
            time1 = 0
            time1_start = 0
            time2 = 0
            time2_start = 0
            time3 = 0
            time3_start = 0
            time4 = 0
            time4_start = 0
            time5 = 0
            time5_start = 0
            time6 = 0
            time6_start = 0
            time7 = 0
            time7_start = 0
            # loop until the rokcket lands
            while (self._rocket.bodies[self._currentBodyIndex].pos[2] > 0.0 or
                    self._rocket.bodies[self._currentBodyIndex].elapsedTime < 0.1):
                time1_start = time.time()
                self._update()
                time1 += time.time() - time1_start
                if self._trajectoryMode == TrajectoryMode.Parachute:
                    self._updateParachute()
                
                if self._rocketType == RocketType.Multi and self._updateDetachment():
                    break
                time2_start = time.time()
                self._updateAerodynamicParameters()
                time2 += time.time() - time2_start
                time3_start = time.time()
                self._updateRopcketProperties()
                time3 += time.time() - time3_start
                time4_start = time.time()
                self._updateExternalForce()
                time4 += time.time() - time4_start
                time5_start = time.time() 
                self._updateRocketDelta()
                time5 += time.time() - time5_start
                time6_start = time.time()
                self._applyDelta()
                time6 += time.time() - time6_start
                time7_start = time.time()
                if self._steps % AppSetting.result.stepSaveInterval == 0:
                    self._organizeResult()
            
                self._steps += 1
                time7 += time.time() - time7_start
            # Save last if need
            if self._steps > 0 and (self._steps - 1) % AppSetting.result.stepSaveInterval != 0:
                self._organizeResult()
            
            self._resultLogger.setBodyFinalPosition(self._currentBodyIndex, self._rocket.bodies[self._currentBodyIndex].pos)
            print([time1, time2, time3, time4, time5, time6, time7])
        return self._resultLogger
        
    def _initializeRocket(self) -> None:
        # Second, Third Rocket(Multiple)
        if self._currentBodyIndex < 2  * self._detachCount:
            self._nextRocket()
            return
        
        # first rocekt
        self._bodyDelta.mass        = self._rocketSpec.bodySpec(0).massInitial
        self._bodyDelta.refLength   = self._rocketSpec.bodySpec(0).CGLengthInitial
        self._bodyDelta.iyz         = self._rocketSpec.bodySpec(0).rollingMomentInertiaInitial
        self._bodyDelta.ix          = 0.02 # TODO : このパラメタの出所
        self._bodyDelta.pos         = np.array([0.0, 0.0, 0.0])
        self._bodyDelta.velocity    = np.array([0.0, 0.0, 0.0])
        self._bodyDelta.omega_b     = np.array([0.0, 0.0, 0.0])
        yaw = np.radians(-(self._environment.railAzimuth - self._mapData.magneticDeclination) + 90) # 東 (x軸正の向き) からの角度 
        pitch = np.radians(self._environment.railElevation)
        roll = 0.0
        
        self._bodyDelta.quat = \
            quaternion.from_euler_angles(yaw, -pitch, 0) # TODO : 計算式要チェック
    
        self._rocket.bodies[self._currentBodyIndex] = deepcopy(self._bodyDelta) # deepcopyしないとidを共有してしまい, deltaに代入するとbodyの方にも代入されてしまう
    
    def _update(self):
        self._windModel.update(self._rocket.bodies[self._currentBodyIndex].pos[2])
        transitions = self._rocketSpec.bodySpec(self._currentBodyIndex).transitions # 代入しなければ参照渡し
        if len(transitions) != 0:
            if transitions[0].time <self._rocket.bodies[self._currentBodyIndex].elapsedTime:
                self._rocket.bodies[self._currentBodyIndex].mass += transitions.mass
                self._rocketSpec.bodySpec(self._currentBodyIndex).aeroCoeffStorage.setConstant(0, transitions[0].Cd, 0)   
                self._rocketSpec.bodySpec(self._currentBodyIndex).transitions = \
                    np.delete(self._rocketSpec.bodySpec(self._currentBodyIndex), 0)
        
    def _updateParachute(self):
        '''パラシュート状態更新関数'''
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        
        detectpeakCondition = THIS_BODY.maxAltitude > THIS_BODY.pos[2] + AppSetting.simulation.detectPeakThreshold
        
        if detectpeakCondition and not THIS_BODY.detectPeak:
            THIS_BODY.detectPeak = True
        
        if THIS_BODY.parachuteOpened:
            return
        
        detectpeak = THIS_BODY_SPEC.parachutes[0].openingType == ParachuteOpeningType.TimeFromDetectPeak
        
        fixedtime          = THIS_BODY_SPEC.parachutes[0].openingType == ParachuteOpeningType.FixedTime
        fixedtimeCondition = THIS_BODY.elapsedTime > THIS_BODY_SPEC.parachutes[0].openingTime
        
        if (detectpeak and detectpeakCondition) or (fixedtime and fixedtimeCondition):
            THIS_BODY.parachuteOpened = True
        
        time_from_detect_peakCondition = \
            THIS_BODY.elapsedTime - THIS_BODY.maxAltitudeTime > THIS_BODY_SPEC.parachutes[0].openingTime
        
        if time_from_detect_peakCondition:
            if not THIS_BODY.waitForOpenPara and detectpeakCondition:
                THIS_BODY.waitForOpenPara = True
            if THIS_BODY.waitForOpenPara and time_from_detect_peakCondition:
                THIS_BODY.parachuteOpened = True
                THIS_BODY.waitForOpenPara = True
    
    def _updateDetachment(self) -> bool:
        '''分離状態更新関数'''
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        detachCondition = False
        
        match self._detachType:
            case DetachType.BurningFinished:
                detachCondition = THIS_BODY_SPEC.engine.didCombustion(THIS_BODY.elapsedTime)
            case DetachType.Time:
                detachCondition = THIS_BODY.elapsedTime >= self._detachTime
            case DetachType.SyncPara:
                detachCondition = THIS_BODY.parachuteOpened
            case DetachType.DoNotDetach:
                return False
        
        if detachCondition and self._detachCount < 1: # if need rocket4, 5, 6, ..., this code should be cahnged
            # initialize separated bodies
            detach : Body = Body()
            detach.ix       = 0.02
            detach.pos      = THIS_BODY.pos
            detach.velocity = THIS_BODY.velocity
            detach.omega_b  = np.array([0.0, 0.0, 0.0])
            detach.quat     = THIS_BODY.quat
            
            # TODO : 分離時の計算
            # Prologueではエンジンから0.2秒間上部ボディに推力を与える処理がコメントアウトされていた.

            self._rocket.bodies[self._currentBodyIndex + 1] = detach 
            nextBody1 : Body = self._rocket.bodies[self._currentBodyIndex + 1] # ミュータブルオブジェクトは参照渡し
            # nextBody1           = detach # これだと参照が変わってしまい, 元の配列は不変
            nextBody1.mass      = self._rocketSpec.bodySpec(self._currentBodyIndex + 1).massInitialmassInitial
            nextBody1.refLength = self._rocketSpec.bodySpec(self._currentBodyIndex + 1).CGLengthInitial
            nextBody1.iyz       = self._rocketSpec.bodySpec(self._currentBodyIndex + 1).rollingMomentInertiaInitial
            
            self._rocket.bodies[self._currentBodyIndex + 2] = detach 
            nextBody2 : Body = self._rocket.bodies[self._currentBodyIndex + 1] # ミュータブルオブジェクトは参照渡し
            nextBody2.mass      = self._rocketSpec.bodySpec(self._currentBodyIndex + 1).massInitialmassInitial
            nextBody2.refLength = self._rocketSpec.bodySpec(self._currentBodyIndex + 1).CGLengthInitial
            nextBody2.iyz       = self._rocketSpec.bodySpec(self._currentBodyIndex + 1).rollingMomentInertiaInitial
        
            self._detachCount += 1
            
            return True
        
        return False
    
    def _updateAerodynamicParameters(self) -> None:
        '''空力特性更新関数'''
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        airspeed = quaternion.from_vector_part(THIS_BODY.velocity - self._windModel.wind) # 地上座標系における風速 (Quaternion)
        THIS_BODY.airspeed_b = (THIS_BODY.quat.conj() * airspeed * THIS_BODY.quat).imag 
        
        THIS_BODY.attackAngle = \
            np.arctan(norm(THIS_BODY.airspeed_b[1:]) / (THIS_BODY.airspeed_b[0] + 1e-16))
        
        THIS_BODY.aeroCoef = \
            THIS_BODY_SPEC.aeroCoeffStorage.valueIn(norm(THIS_BODY.airspeed_b),
                                                    THIS_BODY.attackAngle,
                                                    THIS_BODY_SPEC.engine.didCombustion(THIS_BODY.elapsedTime))
        
        alpha = np.arctan(THIS_BODY.airspeed_b[2] / (THIS_BODY.airspeed_b[0] + 1e-16))
        beta  = np.arctan(THIS_BODY.airspeed_b[1] / (THIS_BODY.airspeed_b[0] + 1e-16))
        
        THIS_BODY.Cnp = THIS_BODY.aeroCoef.Cna * alpha
        THIS_BODY.Cny = THIS_BODY.aeroCoef.Cna * beta
        
        THIS_BODY.Cmqp = THIS_BODY_SPEC.Cmq
        THIS_BODY.Cmqy = THIS_BODY_SPEC.Cmq
    
    def _updateRopcketProperties(self) -> None:
        '''質量・圧力中心・慣性モーメントの微小変化量更新関数'''
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        
        if THIS_BODY_SPEC.engine.isCombusting(THIS_BODY.elapsedTime):
            self._bodyDelta.mass = \
                (THIS_BODY_SPEC.massFinal - THIS_BODY_SPEC.massInitial) / THIS_BODY_SPEC.engine.combustionTime
            self._bodyDelta.refLength = \
                (THIS_BODY_SPEC.CGLengthFinal - THIS_BODY_SPEC.CGLengthInitial) / THIS_BODY_SPEC.engine.combustionTime
            self._bodyDelta.iyz = \
                (THIS_BODY_SPEC.rollingMomentInertiaFinal - THIS_BODY_SPEC.rollingMomentInertiaInitial) / THIS_BODY_SPEC.engine.combustionTime
            self._bodyDelta.ix = (0.01 - 0.02) / THIS_BODY_SPEC.engine.combustionTime
        else:
            self._bodyDelta.mass = 0
            self._bodyDelta.refLength = 0
            self._bodyDelta.iyz = 0
            self._bodyDelta.ix = 0
            
    def _updateExternalForce(self) -> None:
        '''外力更新関数'''
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        
        THIS_BODY.force_b  = np.array([0.0, 0.0, 0.0])
        THIS_BODY.moment_b = np.array([0.0, 0.0, 0.0])
        
        # thrust
        THIS_BODY.force_b[0] += THIS_BODY_SPEC.engine.thrustAt(THIS_BODY.elapsedTime, self._windModel.pressure)
        
        if not THIS_BODY.parachuteOpened:
            # Aero
            preForceCalc : float = 0.5 * self._windModel.density * norm(THIS_BODY.airspeed_b) ** 2 * THIS_BODY_SPEC.bottomArea

            THIS_BODY.force_b -= np.array([
                THIS_BODY.aeroCoef.Cd * preForceCalc * np.cos(THIS_BODY.attackAngle),
                THIS_BODY.Cny * preForceCalc,
                THIS_BODY.Cnp * preForceCalc
            ],) # add aerodynamic force
            
            # Moment
            preMomentCalc : float = 0.25 * self._windModel.density * norm(THIS_BODY.airspeed_b) * THIS_BODY_SPEC.length ** 2 * THIS_BODY_SPEC.bottomArea
            THIS_BODY.moment_b = \
                np.array([
                    0.0, 
                    preMomentCalc * THIS_BODY.Cmqp * THIS_BODY.omega_b[1],
                    preMomentCalc * THIS_BODY.Cmqy * THIS_BODY.omega_b[2]
                ]) + \
                np.array([0.0, THIS_BODY.force_b[2], -THIS_BODY.force_b[1]]) * (THIS_BODY.aeroCoef.Cp - THIS_BODY.refLength)
            
            # gravity
            w = np.quaternion(0.0, 0.0, 0.0, -self._windModel.gravity * THIS_BODY.mass) # 重力の寄与
            THIS_BODY.force_b += (THIS_BODY.quat.conj() * w * THIS_BODY.quat).imag # 正規化しているので \bar{q}^{-1} = {q^{-1}}^{-1}
    
    def _updateRocketDelta(self) -> None:
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        # print(THIS_BODY.pos, THIS_BODY.velocity, THIS_BODY.force_b)
        if norm(THIS_BODY.pos) <= self._environment.railLength and THIS_BODY.velocity[2] >= 0.0: # launch
            if THIS_BODY.force_b[0] < 0:
                self._bodyDelta.pos      = np.array([0.0, 0.0, 0.0])
                self._bodyDelta.velocity = np.array([0.0, 0.0, 0.0])
                self._bodyDelta.omega_b  = np.array([0.0, 0.0, 0.0])
                self._bodyDelta.quat     = np.quaternion(0, 0, 0, 0)
            else:
                THIS_BODY.force_b[1] = 0
                THIS_BODY.force_b[2] = 0 # 機軸方向 (ローンチレール方向) に離床
                self._bodyDelta.pos = THIS_BODY.velocity
                
                self._bodyDelta.velocity = (THIS_BODY.quat * quaternion.from_vector_part(THIS_BODY.force_b) * THIS_BODY.quat.inverse()).imag / THIS_BODY.mass
                
                # print(quaternion.from_vector_part(THIS_BODY.force_b))
                # print(THIS_BODY.quat)
                # print(self._bodyDelta.velocity)
                
                self._bodyDelta.omega_b = np.array([0.0, 0.0, 0.0])
                self._bodyDelta.quat    = np.quaternion(0, 0, 0, 0)
        elif THIS_BODY.parachuteOpened: # parachute opened
            paraSpeed = THIS_BODY.velocity
            drag = 0.5 * self._windModel.density * paraSpeed[2]**2 * THIS_BODY_SPEC.parachutes[THIS_BODY.parachuteIndex].Cd
            
            self._bodyDelta.velocity = np.array([0, 0, drag / THIS_BODY.mass - self._windModel.gravity])
            
            THIS_BODY.velocity[0:2] = self._windModel.wind[0:2] # z軸方向は反映しない
            
            self._bodyDelta.pos = THIS_BODY.velocity
            
            self._bodyDelta.omega_b = np.array([0.0, 0.0, 0.0])
            self._bodyDelta.quat    = np.quaternion(0, 0, 0, 0)
        elif THIS_BODY.pos[2] < -10: # stop simulation
            self._bodyDelta.velocity = np.array([0.0, 0.0, 0.0]) 
        else: # flight
            if not self._rocket.launchClear:
                self._rocket.launchClear = True
                self._resultLogger.setLaunchClear(THIS_BODY)
            
            self._bodyDelta.pos      = THIS_BODY.velocity
            self._bodyDelta.velocity = (THIS_BODY.quat * quaternion.from_vector_part(THIS_BODY.force_b) * THIS_BODY.quat.inverse()).imag / THIS_BODY.mass
            
            self._bodyDelta.omega_b = (THIS_BODY.moment_b / np.array([THIS_BODY.ix, THIS_BODY.iyz, THIS_BODY.iyz]))
            
            self._bodyDelta.quat = THIS_BODY.quat * quaternion.from_vector_part(THIS_BODY.omega_b) * 0.5 # integration
    
    def _applyDelta(self) -> None:
        '''積分関数'''
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        
        # Update rocekt
        THIS_BODY.mass      += self._bodyDelta.mass      * self._dt
        THIS_BODY.refLength += self._bodyDelta.refLength * self._dt
        THIS_BODY.iyz       += self._bodyDelta.iyz       * self._dt
        THIS_BODY.ix        += self._bodyDelta.ix        * self._dt
        THIS_BODY.pos       += self._bodyDelta.pos       * self._dt
        THIS_BODY.velocity  += self._bodyDelta.velocity  * self._dt
        THIS_BODY.omega_b   += self._bodyDelta.omega_b   * self._dt
        THIS_BODY.quat      += self._bodyDelta.quat      * self._dt
        
        if np.nonzero(THIS_BODY.quat):
            THIS_BODY.quat = THIS_BODY.quat.normalized()
        
        THIS_BODY.elapsedTime += self._dt
        self._rocket.timeFromLaunch += self._dt
    
    def _organizeResult(self) -> None:
        THIS_BODY : Body = self._rocket.bodies[self._currentBodyIndex] # ミュータブルオブジェクトは参照渡し
        THIS_BODY_SPEC : BodySpecification = self._rocketSpec.bodySpec(self._currentBodyIndex)
        
        self._resultLogger.update(self._currentBodyIndex,
                                  self._rocket,
                                  THIS_BODY,
                                  self._windModel,
                                  THIS_BODY_SPEC.engine.isCombusting(THIS_BODY.elapsedTime))
        if THIS_BODY.maxAltitude < THIS_BODY.pos[2]:
            THIS_BODY.maxAltitude     = THIS_BODY.pos[2]
            THIS_BODY.maxAltitudeTime = THIS_BODY.elapsedTime
        
    def _nextRocket(self) -> None:
        '''Prepare the next rocket (multi rocket)'''
        self._currentBodyIndex += 1
        self._resultLogger.pushBody()    