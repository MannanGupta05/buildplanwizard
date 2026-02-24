"""
New extractors that work with whole images instead of YOLO-detected regions.

These extractors return -1 from _get_target_class_ids() to indicate that the
entire input image should be passed to the model rather than cropped regions.
"""

from .area_extraction import AreaExtractor
from .room_extraction import RoomExtractor
from .setback_floors_extraction import SetbackFloorsExtractor
from .staircase_extraction import StaircaseExtractor
from .height_kitchen_bathroom_extraction import HeightKitchenBathroomExtractor

__all__ = [
    'AreaExtractor',
    'RoomExtractor', 
    'SetbackFloorsExtractor',
    'StaircaseExtractor',
    'HeightKitchenBathroomExtractor'
]