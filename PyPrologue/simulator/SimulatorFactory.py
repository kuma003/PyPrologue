'''
SimulatorBaseクラスの生成を担う
'''

from PyPrologue.app.CommandLine import *
from PyPrologue.simulator.Simulator import *
from PyPrologue.solver.Solver import *


from pathlib import Path
import glob

class SimulatorFactory:    
    _specDirPath : Path = Path("input/spec")
    
    @staticmethod
    def Create() -> SimulatorBase:
        try:
            # Specification json file
            specFilePath = SimulatorFactory._setSpecFile()
            file = open(specFilePath) # 外部で try-except-finnally を使っているので with は使わず自前で処理する
            specJson = json.load(file)
            
            # Specification name
            specName = specFilePath.stem
            
            # Setup simulator
            simulationSetting : SimulatorBase.SimulationSetting = SimulatorFactory._setupSimulator(specJson)
            
            # Create simulation instance
            if AppSetting.windModel.type == WindModelType.Real or AppSetting.windModel.type == WindModelType.NoWind or \
                simulationSetting.simulationMode == SimulationMode.Detail:
                return DetailSimulator(specName=specName, specJson=specJson, setting=simulationSetting) # finallyの後にこれが実行されることに注意
            else:
                raise RuntimeError("SimulatorFactory::Create(): Detected unhandled return path.")  # TODO : ScatterSimulatorの実装
        except Exception as e:
            PrintInfo(PrintInfoType.Error, e)
        finally:
            try:
                file.close()  # file が存在すればデストラクタを呼んで正常にクロース
            except:
                pass
        return None
    
    @staticmethod
    def _setSpecFile() -> Path:
        specificationFiles = \
            [file.name for file in SimulatorFactory._specDirPath.glob("*.json")]
        
        if len(specificationFiles) == 0:
            raise RuntimeError("Specification file not found in input/spec/.")
        
        Question("Set Specification File", *specificationFiles)
        
        inputIndex = InputIndex(len(specificationFiles))
        return SimulatorFactory._specDirPath / specificationFiles[inputIndex - 1]
    
    @staticmethod
    def _setSimulationMode() -> SimulationMode:
        Question("Set Simulation Mode", "Scatter Mode", "Detail Mode")
        return SimulationMode(InputIndex(2))
    
    @staticmethod
    def _setTrajectoryMode() -> TrajectoryMode:
        Question("Set Falling Type", "Trajectory", "Parachute")
        return TrajectoryMode(InputIndex(2))
    
    @staticmethod
    def _setWindCondition() -> tuple[float, float]:
        windSpeed     = InputFloat(prompt="Input Wind Velocity[m/s]")
        windDirection = InputFloat(prompt="Input Wind Direction[deg] (North: 0, East: 90)")
        return (windSpeed, windDirection)
    
    @staticmethod
    def _setDetachType() -> DetachType:
        Question("Set Detach Type",
                 "When burning finished",
                 "Specify time",
                 "Concurrently with parachute",
                 "Do not detach")
        return DetachType(InputIndex(4))
    
    @staticmethod
    def _setDetachTime() -> float:
        return InputFloat("Set Detach Time", only_positive=True)
    
    @staticmethod
    def _setupSimulator(specJson : dict) -> SimulatorBase.SimulationSetting:
        setting = SimulatorBase.SimulationSetting()

        if AppSetting.windModel.type != WindModelType.Real and AppSetting.windModel.type != WindModelType.NoWind:
            setting.simulationMode = SimulatorFactory._setSimulationMode()
        
        setting.trajectoryMode = SimulatorFactory._setTrajectoryMode()
        
        # set wind condition if need
        if setting.simulationMode == SimulationMode.Detail and \
            AppSetting.windModel.type != WindModelType.Real and AppSetting.windModel.type != WindModelType.NoWind:
            setting.windSpeed, setting.windDirection = SimulatorFactory._setWindCondition()
        
        # setup multiple rocket
        if RocketSpecification.isMultipleRocket(specJson):
            PrintInfo(PrintInfoType.Information, "This is Multiple Rocket")
            setting.detachType = SimulatorFactory._setDetachType()
            if setting.detachType == DetachType.Time:
                setting.detachTime = SimulatorFactory._setDetachTime()
        
        return setting