import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class PlotAreaExtractor(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for plot area extraction."""
        return {
            "total_plot_area": example["total_plot_area"],
            "total_covered_area": example["total_covered_area"],
            "far": example["far"]
        }
    
    def _get_target_class_ids(self):
        """Plot area extraction targets class_id 1."""
        return [1]
    
    def _get_query_text(self):
        """Query text for plot area extraction."""
        return "Give total_plot_area, total_covered_area and far as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for plot area."""
        # Ensure values are in list format as expected by validation system
        def ensure_list(value):
            if value is None:
                return [0]
            elif isinstance(value, list):
                return value
            else:
                return [value]
        
        return {
            "total_plot_area": ensure_list(data_dict.get('total_plot_area')),
            "total_covered_area": ensure_list(data_dict.get('total_covered_area')),
            "far": ensure_list(data_dict.get('far'))
        }
    
    def _format_final_output(self, results):
        """Format final output for plot area extraction."""
        return results  # Results are already in correct dict format
    

    