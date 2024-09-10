'''
結果保存用関数
'''

from PyPrologue.app.AppSetting import *
from PyPrologue.app.CommandLine import *
from PyPrologue.result.SimuResult import *
from PyPrologue.solver.Solver import *

import numpy as np
from numpy.linalg import norm
from pathlib import Path
from io import *
import itertools # 二重リスト展開用

class ResultSaver:
    headerDetail : list[str] = [
        # general
        "time_from_launch[s]",
        "elapsed_time[s]",
        # boolean
        "launch_clear?",
        "combusting?",
        "para_opened?",
        # air
        "air_density[kg/m3]",
        "gravity[m/s2]",
        "pressure[Pa]",
        "temperature[C]",
        "wind_x[m/s]",
        "wind_y[m/s]",
        "wind_z[m/s]",
        # body
        "mass[kg]",
        "Cg_from_nose[m]",
        "inertia moment pitch & yaw[kg*m2]",
        "inertia moment roll[kg*m2]",
        "attack angle[rad]",
        "altitude[m]",
        "velocity[m/s]",
        "airspeed[m/s]",
        "accel[m/s2]",
        "longitudinal accel[m/s2]",
        "normal_force[N]",
        "Cnp",
        "Cny",
        "Cmqp",
        "Cmqy",
        "Cp_from_nose[m]",
        "Cd",
        "Cna",
        # position
        "latitude",
        "longitude",
        "downrange[m]",
        # calculated
        "Fst[%]",
        "dynamic_pressure[Pa]"
    ]    
    headerSumamry = [
        "wind_speed[m/s]",
        "wind_dir[deg]",
        "launch_clear_time[s]",
        "launch_clear_vel[m/s]",
        "max_altitude[m]",
        "max_altitude_time[s]",
        "max_velocity[m/s]",
        "max_airspeed[m/s]",
        "max_normal_force_rising[N]"
    ]
    
    @staticmethod
    def SaveScatter(dir : Path | str, result : np.ndarray[SimuResultSummary]) -> None:
        if not isinstance(dir, Path): dir = Path(dir)
        if not dir.is_dir: return # error
        
        ResultSaver._write_summary_scatter(dir, result)
    
    @staticmethod
    def SaveDetail(dir : Path | str, result : SimuResultSummary) -> None:
        if not isinstance(dir, Path): dir = Path(dir)
        if not dir.is_dir: return # error
        
        # Save detail
        # write time-series data of all bodies
        bodyCount = len(result.bodyFinalPositions)
        for i in range(bodyCount):
            path : Path = dir/f"detail_body{i+1}.csv"
            with open(path, mode="w") as f:
                ResultSaver._write_body_result(f, result.bodyResults[i].steps)
    
    @staticmethod
    def _write_body_result(f : TextIOWrapper, stepResult : np.ndarray[SimuResultStep]) -> None:
        # write header
        f.write(",".join(ResultSaver.headerDetail))
        
        f.write("\n")
        
        for step, _ in zip(stepResult, progress_bar(len(stepResult))):
            step : SimuResultStep
            line = ",".join(map(str, [
                # general
                step.gen_timeFromLaunch, step.gen_elapsedTime,
                
                # boolean
                step.launchClear, step.combusting, step.parachuteOpened,
                
                # air
                step.air_density, step.air_gravity, step.air_pressure,
                step.air_temperature, step.air_wind[0], step.air_wind[1], step.air_wind[2],
                
                # body
                step.rocket_mass, step.rocket_cgLength, step.rocket_iyz, 
                step.rocket_ix, step.rocket_attackAngle,
                step.rocket_pos[2], norm(step.rocket_velocity),
                norm(step.rocket_airspeed_b), norm(step.rocket_force_b) / step.rocket_mass,
                step.rocket_force_b[0] / step.rocket_mass,
                norm(step.rocket_force_b[1:]),
                step.Cnp, step.Cny, step.Cmqp, step.Cmqy,
                step.Cp, step.Cd, step.Cna,
                
                # position
                step.latitude, step.longitude, step.downrange,
                
                # calculated
                step.Fst, step.dynamicPressure
            ]))  # 文字列型にキャストしてからカンマで結合
            f.write(line + "\n") # 書き込み
    
    @staticmethod
    def _write_summary_header(f : TextIOWrapper, bodyCount : int) -> None:
        additional_header = \
            [f"{i}_final_latitude,{i}_final_longitude" for i in range(bodyCount)]
        
        # writeheader
        f.write(",".join(ResultSaver.headerSumamry + additional_header))
        
        f.write("\n")

    @staticmethod
    def _write_summary(f : TextIOWrapper, result : SimuResultSummary) -> None:
        cols = [
            result.windSpeed, result.windDirection,
            result.launchClearTime, norm(result.launchClearVelocity),
            result.maxAltitude, result.detectPeakTime,
            result.maxVelocity, result.maxAirspeed,
            result.maxNormalForceDuringRising
        ]
        cols += list(
            itertools.chain.from_iterable([[pos.latitude, pos.longitude] for pos in result.bodyFinalPositions])
        ) # PrologueではbodyがbodyCountに足りない場合に0で埋めているが，結果は変わらないので省略
        
        f.write(",".join(map(str, cols)) + "\n")
    
    @staticmethod
    def _write_summary_scatter(dir : Path, results : np.ndarray[SimuResultSummary]):
        with open(dir/"summary.csv", mode="w") as f:
            bodyCount = max([len(result.bodyFinalPositions) for result in results])
            
            ResultSaver._write_summary_header(f, bodyCount)
            
            for result in results:
                ResultSaver._write_summary(f, result, bodyCount)
    
    @staticmethod
    def _write_summary_detail(dir : Path, result : SimuResultSummary):
        with open(file=dir/"summary.csv", mode="w") as f:
            ResultSaver._write_summary_header(f, len(result.bodyFinalPositions))
            
            ResultSaver._write_summary(f, result, len(result.bodyFinalPositions))