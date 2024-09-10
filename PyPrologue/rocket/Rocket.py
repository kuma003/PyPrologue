'''
解析に用いる機体のパラメータ
'''
import numpy as np
import quaternion
from PyPrologue.rocket.AeroCoefficient import *
from dataclasses import dataclass, field

@dataclass
class Body:
    # ========================delta exists========================= #
    mass : float = 0                 # mass [kg]
    refLength : float = 0            # length from nose to center of mass[m]
    iyz : float = 0                  # inertia moment of pitching & yawing [kg*m^2]
    ix : float = 0                   # inertia moment of rolling [kg*m^2]
    pos : np.ndarray = 0             # position [m] (ENU coordinate)
    velocity : np.ndarray = 0        # velocity [m/s] (ground speed)
    omega_b : np.ndarray = 0        # angular velocity (roll,pitch,yaw)
    quat : quaternion.quaternion = field(default_factory=lambda: np.quaternion(0, 0, 0, 0)) # quaternion
    
    # ========================delta not exists===================== #
    aeroCoef : AeroCoefficient = field(default_factory=AeroCoefficient)
    Cnp : float = 0; Cny : float = 0
    Cmqp : float = 0; Cmqy : float = 0
    force_b : np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    moment_b : np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    
    # status
    elapsedTime : float = 0.0  # [s]
    parachuteIndex : int = 0
    parachuteOpened : bool = False
    waitForOpenPara : bool = False
    detectPeak : bool = False
    maxAltitude : float     = 0.0  # [m]
    maxAltitudeTime : float = 0.0  # [s]
    
    # calculated
    airspeed_b : np.ndarray = field(default_factory=lambda: np.array([0.0, 0.0, 0.0]))
    attackAngle : float = 0
    

@dataclass
class Rocket:
    # rocket1, rocket2+ , rocket3, ...
    bodies : np.ndarray = field(default_factory=lambda: np.array([], dtype=Body))
    
    timeFromLaunch : float = 0.0  # [s]
    launchClear : bool = False