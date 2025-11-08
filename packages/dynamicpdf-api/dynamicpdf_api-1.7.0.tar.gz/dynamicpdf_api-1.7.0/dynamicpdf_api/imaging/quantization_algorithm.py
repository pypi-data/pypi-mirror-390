from enum import Enum

class QuantizationAlgorithm(Enum):
    Octree = 'Octree'
    WebSafe = 'WebSafe'
    Werner = 'Werner'
    Wu = 'Wu'