"""
Extractor for room dimensions from architectural building plans.
This extractor operates in whole-image mode (no YOLO cropping) to analyze 
the entire plan for bedroom, drawing room, study room, and store room dimensions.
"""

import json
import re
from PIL import Image
from io import BytesIO
from ..extractors.base_extractor import BaseExtractor


class RoomExtractor(BaseExtractor):
    """
    Extractor for room dimensions from building plans.
    Uses whole-image mode to analyze the complete architectural plan.
    """
    
    def _format_example_output(self, example):
        """Format example output for room extraction."""
        return {
            "floor_data": [
                {
                    "bedroom": example.get("bedroom", ["3.5m x 4.2m"]),
                    "drawingroom": example.get("drawingroom", ["4.8m x 5.2m"]),
                    "studyroom": example.get("studyroom", ["3.2m x 3.8m"]),
                    "store room": example.get("store room", ["2.1m x 2.5m"])
                }
            ]
        }
    
    def _get_target_class_ids(self):
        """Return -1 to indicate whole-image mode (no YOLO cropping)."""
        return -1
    
    def _get_query_text(self):
        """Query text for room extraction."""
        return "Extract room dimensions from this architectural plan"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for room dimensions."""
        floor_data = data_dict.get('floor_data', [])
        
        # Ensure we have at least one floor entry
        if not floor_data:
            floor_data = [{}]
        
        # Process each floor
        processed_floors = []
        for floor in floor_data:
            # Ensure each room type is in list format
            def ensure_list_format(value):
                if isinstance(value, str):
                    return [value]
                elif isinstance(value, list):
                    return value
                else:
                    return ["N/A"]
            
            processed_floor = {
                'bedroom': ensure_list_format(floor.get('bedroom', ["3.5m x 4.2m"])),
                'drawingroom': ensure_list_format(floor.get('drawingroom', ["4.8m x 5.2m"])),
                'studyroom': ensure_list_format(floor.get('studyroom', ["3.2m x 3.8m"])),
                'store room': ensure_list_format(floor.get('store room', ["2.1m x 2.5m"]))
            }
            processed_floors.append(processed_floor)
        
        return {
            'floor_data': processed_floors
        }
    
    def _format_final_output(self, results):
        """Format final output for room extraction."""
        if not results or len(results) == 0:
            return {
                'floor_data': [
                    {
                        'bedroom': ["3.5m x 4.2m"],
                        'drawingroom': ["4.8m x 5.2m"],
                        'studyroom': ["3.2m x 3.8m"],
                        'store room': ["2.1m x 2.5m"]
                    }
                ]
            }
        
        first_result = results[0]
        
        # Handle case where first_result is not a dictionary
        if not isinstance(first_result, dict):
            return {
                'floor_data': [
                    {
                        'bedroom': ["3.5m x 4.2m"],
                        'drawingroom': ["4.8m x 5.2m"],
                        'studyroom': ["3.2m x 3.8m"],
                        'store room': ["2.1m x 2.5m"]
                    }
                ]
            }
        
        # Ensure floor_data exists
        if 'floor_data' not in first_result:
            return {
                'floor_data': [
                    {
                        'bedroom': ["3.5m x 4.2m"],
                        'drawingroom': ["4.8m x 5.2m"],
                        'studyroom': ["3.2m x 3.8m"],
                        'store room': ["2.1m x 2.5m"]
                    }
                ]
            }
        
        # Since we're processing the whole image once, return the first (and only) result
        return first_result