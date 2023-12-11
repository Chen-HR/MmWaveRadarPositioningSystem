import time
import datetime

from Ti_MmWave_Demo_Driver import Ti_MmWave as MmWaveDevice
from MmWaveRadarSystem import MmWaveRadarSystem, AreaLimit_3d, Range
import HAClusteringTool
from . import CoordinateSystem_Conversion_3D

import matplotlib.pyplot
import matplotlib.collections
import matplotlib.animation

class MmWaveRadarCompositeSystem:
  def __init__(self, radarSystems: list[MmWaveRadarSystem] = list(), converters: list[CoordinateSystem_Conversion_3D.Conversion_CoordinateSystem_3D] = list(), log_enabled: bool = False):
    self.radarSystems: list[MmWaveRadarSystem] = radarSystems
    self.converters: list[CoordinateSystem_Conversion_3D.Conversion_CoordinateSystem_3D] = converters
    self.log_enabled = log_enabled
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarCompositeSystem.init({radarSystems}, {converters})")
  def append(self, radarSystem: MmWaveRadarSystem, converter: CoordinateSystem_Conversion_3D.Conversion_CoordinateSystem_3D):
    self.radarSystems.append(radarSystem)
    self.converters.append(converter)
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarCompositeSystem.append({radarSystem}, {converter})")
  def start(self):
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarCompositeSystem.start()")
    [radarSystem.start() for radarSystem in self.radarSystems]
  def stop(self):
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarCompositeSystem.stop()")
    [radarSystem.stop() for radarSystem in self.radarSystems]
  def detectedPoints(self) -> list[tuple]:
    # radarSystems_detectedPoints = [converter.converts(radarSystem.detectedPoints(False)) for (radarSystem, converter) in zip(self.radarSystems, self.converters)]
    detectedPoints: list[tuple] = list()
    for radarSystem, converter in zip(self.radarSystems, self.converters):
      detectedPoints += converter.converts(radarSystem.detectedPoints(False))
    return detectedPoints
  def __del__(self):
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarCompositeSystem.del()")
    for radarSystem in self.radarSystems: del radarSystem

class MmWaveRadarPositioningSystem:
  def __init__(self, compositeSystem: MmWaveRadarCompositeSystem, clusterRadius: int | float = 0.75, interval_ms: int = 1000, log_enabled: bool = False):
    self.compositeSystem: MmWaveRadarCompositeSystem = compositeSystem
    self.clusterRadius: int | float = clusterRadius
    self.interval_ms: int = interval_ms
    self.log_enabled: bool = log_enabled
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarPositioningSystem.init({compositeSystem}, {clusterRadius})")
  def start(self):
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarPositioningSystem.start()")
    self.compositeSystem.start()
  def stop(self):
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarPositioningSystem.stop()")
    self.compositeSystem.stop()
  def positioning(self, clusterRadius: int | float | None = None, useVirtual: bool = False, associateVirtual: bool = False , withWeight: bool = False, virtualWeight = None, sourceWeight = None):
    self.clusterRadius = clusterRadius if clusterRadius is not None else self.clusterRadius
    return HAClusteringTool.clustering_centers(self.compositeSystem.detectedPoints(), self.clusterRadius, useVirtual=useVirtual, associateVirtual=associateVirtual, withWeight=withWeight, virtualWeight=virtualWeight, sourceWeight=sourceWeight)
  def __del__(self):
    if self.log_enabled: print(f"[{datetime.datetime.now()}] MmWaveRadarPositioningSystem.del()")
    self.stop()
    del self.compositeSystem

if __name__ == "__main__":
  detectionLimit = AreaLimit_3d(Range(-5, 5), Range(-5, 5), Range(-5, 5))

  mmWaveRadarSystem = MmWaveRadarSystem(MmWaveDevice("xWR14xx", "COM3", "COM4", log_echo=True, log_enable=True), "Ti_MmWave_Demo_Driver\Profile\Profile-4.cfg", log_enable=True)
  mmWaveRadarCompositeSystem = MmWaveRadarCompositeSystem([mmWaveRadarSystem], 
                                                          [CoordinateSystem_Conversion_3D.Conversion_CoordinateSystem_3D(CoordinateSystem_Conversion_3D.Rotation(0, 0, 180), CoordinateSystem_Conversion_3D.Translation(0, 0, 0))], 
                                                          log_enabled = True)
  mmWaveRadarPositioningSystem = MmWaveRadarPositioningSystem(mmWaveRadarCompositeSystem, log_enabled = True)
  mmWaveRadarPositioningSystem.start()

  def plot_3d(detectionLimit: AreaLimit_3d, mmWaveRadarPositioningSystem: MmWaveRadarPositioningSystem):
    figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()
    figure.set_label("Millimeter Wave Radar detection chart")
    axes: matplotlib.pyplot.Axes = figure.add_subplot(111, projection="3d")
    def update(frame, axes: matplotlib.pyplot.Axes, mmWaveRadarPositioningSystem: MmWaveRadarPositioningSystem):
      detectedPoints = mmWaveRadarPositioningSystem.compositeSystem.detectedPoints()
      detectedPoints_ = tuple(zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
      positioningPoints = mmWaveRadarPositioningSystem.positioning(useVirtual=True, associateVirtual=True)
      positioningPoints_ = tuple(zip(*positioningPoints)) if len(positioningPoints) != 0 else ([], [], [])
      axes.clear()
      axes.set_title("Detection distribution map")
      axes.set(xlim3d=(detectionLimit.x.min, detectionLimit.x.max), xlabel="X (Unit: Meter)")
      axes.set(ylim3d=(detectionLimit.y.min, detectionLimit.y.max), ylabel="Y (Unit: Meter)")
      axes.set(zlim3d=(detectionLimit.z.min, detectionLimit.z.max), zlabel="Z (Unit: Meter)")
      axes.scatter(detectedPoints_[0], detectedPoints_[1], detectedPoints_[2], c="b", alpha=0.5, label="Detected Points")
      axes.scatter(positioningPoints_[0], positioningPoints_[1], positioningPoints_[2], c="r", alpha=1, label="Cluster Positioning")
      axes.grid(True)
      axes.legend()
    animation = matplotlib.animation.FuncAnimation(figure, update, fargs=(axes, mmWaveRadarPositioningSystem), interval=mmWaveRadarPositioningSystem.interval_ms, cache_frame_data=False)
    matplotlib.pyplot.show()

  def plot_2d(detectionLimit: AreaLimit_3d, mmWaveRadarPositioningSystem: MmWaveRadarPositioningSystem):
    figure: matplotlib.pyplot.Figure = matplotlib.pyplot.figure()
    figure.set_label("Millimeter Wave Radar detection chart")
    axes: matplotlib.pyplot.Axes = figure.add_subplot(111)
    def update(frame, axes: matplotlib.pyplot.Axes, mmWaveRadarPositioningSystem: MmWaveRadarPositioningSystem):
      detectedPoints = mmWaveRadarPositioningSystem.compositeSystem.detectedPoints()
      detectedPoints_ = tuple(zip(*detectedPoints)) if len(detectedPoints) != 0 else ([], [], [])
      positioningPoints = mmWaveRadarPositioningSystem.positioning(useVirtual=True, associateVirtual=True)
      positioningPoints_ = tuple(zip(*positioningPoints)) if len(positioningPoints) != 0 else ([], [], [])
      axes.clear()
      axes.set_title("Detection distribution map")
      axes.set_xlabel("X (Unit: Meter)")
      axes.set_ylabel("Y (Unit: Meter)")
      axes.set_xlim(detectionLimit.x.min, detectionLimit.x.max)
      axes.set_ylim(detectionLimit.y.min, detectionLimit.y.max)
      axes.scatter(detectedPoints_[0], detectedPoints_[1], c="b", alpha=0.5, label="Detected Points")
      axes.scatter(positioningPoints_[0], positioningPoints_[1], c="r", alpha=1, label="Cluster Positioning")
      axes.legend()
    animation = matplotlib.animation.FuncAnimation(figure, update, fargs=(axes, mmWaveRadarPositioningSystem), interval=mmWaveRadarPositioningSystem.interval_ms, cache_frame_data=False)
    matplotlib.pyplot.show()

  plot_3d(detectionLimit, mmWaveRadarPositioningSystem)
  plot_2d(detectionLimit, mmWaveRadarPositioningSystem)

  mmWaveRadarPositioningSystem.stop()

  del mmWaveRadarPositioningSystem
