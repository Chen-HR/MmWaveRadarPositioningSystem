import numpy

class Rotation:
  """
  # Rotation Matrix
  The rotation matrix is a 3x3 matrix that represents the rotation transformation in three-dimensional space. 
  The matrix is constructed based on the Euler angles of rotation around the X, Y, and Z axes. 
  The Euler angles are specified as rotations around the X-axis (roll), Y-axis (pitch), and Z-axis (yaw).
  The units used are degrees.
  """
  def __init__(self, x, y, z):
    self.rotation = numpy.radians((x, y, z))
    x, y, z = self.rotation
    self.matrix: numpy.array = numpy.array([
      [ numpy.cos(y) *  numpy.cos(z), -numpy.cos(x) * numpy.sin(z) + numpy.sin(x) * numpy.sin(y) * numpy.cos(z),  numpy.sin(x) * numpy.sin(z) + numpy.cos(x) * numpy.sin(y) * numpy.cos(z)],
      [ numpy.cos(y) *  numpy.sin(z),  numpy.cos(x) * numpy.cos(z) + numpy.sin(x) * numpy.sin(y) * numpy.sin(z), -numpy.sin(x) * numpy.cos(z) + numpy.cos(x) * numpy.sin(y) * numpy.sin(z)],
      [-numpy.sin(y)                ,  numpy.sin(x) * numpy.cos(y)                                             ,  numpy.cos(x) * numpy.cos(y)                                             ]
    ])

class Translation:
  def __init__(self, x, y, z):
    self.translation = (x, y, z)
    self.matrix: numpy.array = numpy.array((x, y, z))

class Conversion_CoordinateSystem_3D:
  def __init__(self, rotation: Rotation, translation: Translation):
    self.rotation = rotation
    self.translation = translation
  def convert(self, point: tuple) -> tuple:
    return tuple(numpy.dot(self.rotation.matrix, numpy.array(point)) + self.translation.matrix)
  def converts(self, points: list[tuple]) -> list[tuple]:
    return [tuple(numpy.dot(self.rotation.matrix, numpy.array(object=point)) + self.translation.matrix) for point in points]
  
if __name__ == "__main__":
  relative_coords = (1, 2, 3)
  converter = Conversion_CoordinateSystem_3D(Rotation(45, 30, 60), Translation(5, 5, 5))

  absolute_coords = converter.convert(relative_coords)
  print("Relative Coordinates:", relative_coords)
  print("Absolute Coordinates:", absolute_coords)
