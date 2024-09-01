'''
解析に用いる機体のパラメータ
'''
import numpy as np
import quaternion
from PyPrologue.rocket.AeroCoefficient import *
from dataclasses import dataclass

@dataclass
class Body:
    # ========================delta exists========================= #
    mass : float                 # mass [kg]
    refLength : float            # length from nose to center of mass[m]
    iyz : float                  # inertia moment of pitching & yawing [kg*m^2]
    ix : float                   # inertia moment of rolling [kg*m^2]
    pos : np.ndarray             # position [m] (ENU coordinate)
    velocity : np.ndarray        # velocity [m/s] (ground speed)
    omega_b : np.ndarray         # angular velocity (roll,pitch,yaw)
    quat : quaternion.quaternion # quaternion
    
    # ========================delta not exists===================== #
    aeroCoef : AeroCoefficient
    Cnp : float; Cny : float
    Cmqp : float; Cmqy : float
    force_b : np.ndarray
    moment_b : np.ndarray
    
    # status
    elapsedTime : float = 0.0  # [s]
    parachuteIndex : int = 0
    parachuteOpened : bool = False
    waitforOpenPara : bool = False
    detectPeak : bool = False
    maxAltitude : float     = 0.0  # [m]
    maxAltitudeTime : float = 0.0  # [s]
    
    # calculated
    airspeed_b : np.ndarray
    attackAngle : float

@dataclass
class Rocket:
    # rocket1, rocket2, rocket3, ...
    bodies : np.ndarray
    
    timeFromLaunch : float = 0.0  # [s]
    launchClear : bool = False