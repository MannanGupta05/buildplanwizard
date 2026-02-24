"""
Extractor for plot area, ground coverage, total covered area, and FAR from architectural building plans.
This extractor operates in whole-image mode (no YOLO cropping) to analyze 
the entire plan for area calculations and Floor Area Ratio.
"""

import json
import re
from PIL import Image
from io import BytesIO
from ..extractors.base_extractor import BaseExtractor


class AreaExtractor(BaseExtractor):
    """
    Extractor for area-related metrics from building plans.
    Uses whole-image mode to analyze the complete architectural plan.
    """
    
    def _format_example_output(self, example):
        """Format example output for area extraction."""
        return {
            "floor_data": [],
            "plot_data": {
                "total_plot_area": example.get("total_plot_area", 0.0),
                "ground_covered_area": example.get("ground_covered_area", 0.0),
                "total_covered_area": example.get("total_covered_area", 0.0),
                "far": example.get("far", 0.0)
            }
        }
    
    def _get_target_class_ids(self):
        """Return -1 to indicate whole-image mode (no YOLO cropping)."""
        return -1
    
    def _get_query_text(self):
        """Query text for area extraction."""
        return "Extract area values and FAR from this architectural plan"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for area information."""
        plot_data = data_dict.get('plot_data', {})
        
        # Extract and validate numeric values
        def safe_float_conversion(value, default=0.0):
            """Safely convert value to float."""
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                return float(value)
            elif isinstance(value, list) and len(value) > 0:
                return safe_float_conversion(value[0], default)
            else:
                return default
        
        total_plot_area = safe_float_conversion(plot_data.get('total_plot_area', 0.0))
        ground_covered_area = safe_float_conversion(plot_data.get('ground_covered_area', 0.0))
        total_covered_area = safe_float_conversion(plot_data.get('total_covered_area', 0.0))
        far = safe_float_conversion(plot_data.get('far', 0.0))
        
        results = {
            'floor_data': [],
            'plot_data': {
                'total_plot_area': total_plot_area,
                'ground_covered_area': ground_covered_area,
                'total_covered_area': total_covered_area,
                'far': far
            }
        }

        return results
    
    def _format_final_output(self, results):
        """Format final output for area extraction."""
        if not results or len(results) == 0:
            return {
                'floor_data': [],
                'plot_data': {
                    'total_plot_area': 0.0,
                    'ground_covered_area': 0.0,
                    'total_covered_area': 0.0,
                    'far': 0.0
                }
            }
        
        first_result = results[0]
        
        # Handle case where first_result is not a dictionary
        if not isinstance(first_result, dict):
            return {
                'floor_data': [],
                'plot_data': {
                    'total_plot_area': 0.0,
                    'ground_covered_area': 0.0,
                    'total_covered_area': 0.0,
                    'far': 0.0
                }
            }
        
        # Ensure plot_data exists
        if 'plot_data' not in first_result:
            return {
                'floor_data': [],
                'plot_data': {
                    'total_plot_area': 0.0,
                    'ground_covered_area': 0.0,
                    'total_covered_area': 0.0,
                    'far': 0.0
                }
            }
        
        # Since we're processing the whole image once, return the first (and only) result
        return first_result
