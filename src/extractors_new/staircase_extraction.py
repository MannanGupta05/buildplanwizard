"""
Extractor for staircase dimensions from architectural building plans.
This extractor operates in whole-image mode (no YOLO cropping) to analyze 
the entire plan for staircase width, tread, and riser dimensions.
"""

import json
import re
from PIL import Image
from io import BytesIO
from ..extractors.base_extractor import BaseExtractor


class StaircaseExtractor(BaseExtractor):
    """
    Extractor for staircase dimensions from building plans.
    Uses whole-image mode to analyze the complete architectural plan.
    """
    
    def _format_example_output(self, example):
        """Format example output for staircase extraction."""
        return {
            "staircase_riser": example.get("staircase_riser", ["0.18m"]),
            "staircase_tread": example.get("staircase_tread", ["0.25m"]),
            "staircase_width": example.get("staircase_width", ["1.2m"])
        }
    
    def _get_target_class_ids(self):
        """Return -1 to indicate whole-image mode (no YOLO cropping)."""
        return -1
    
    def _get_query_text(self):
        """Query text for staircase extraction."""
        return "Extract staircase dimensions from this architectural plan"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for staircase dimensions."""
        # Ensure all staircase values are in list format
        def ensure_list_format(value):
            if isinstance(value, str):
                return [value]
            elif isinstance(value, list):
                return value
            else:
                return ["N/A"]
        
        staircase_riser = ensure_list_format(data_dict.get('staircase_riser', ["N/A"]))
        staircase_tread = ensure_list_format(data_dict.get('staircase_tread', ["N/A"]))
        staircase_width = ensure_list_format(data_dict.get('staircase_width', ["N/A"]))
        
        return {
            'staircase_riser': staircase_riser,
            'staircase_tread': staircase_tread,
            'staircase_width': staircase_width
        }
    
    def _format_final_output(self, results):
        """Format final output for staircase extraction."""
        if not results or not results[0] or (not results[0].get('staircase_riser') and not results[0].get('staircase_tread') and not results[0].get('staircase_width')):
            return {
                'staircase_riser': ["N/A"],
                'staircase_tread': ["N/A"],
                'staircase_width': ["N/A"]
            }
        
        # Since we're processing the whole image once, return the first (and only) result
        return results[0]