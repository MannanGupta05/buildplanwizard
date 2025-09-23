import json
import re
from PIL import Image
from io import BytesIO
from .base_extractor import BaseExtractor

class HeightPlinthExtractor(BaseExtractor):
    
    def _format_example_output(self, example):
        """Format example for height and plinth extraction."""
        return {
            "height": example["height"],
            "plinth level": example["plinth level"]
        }
    
    def _get_target_class_ids(self):
        """Height/plinth extraction targets class_id 3."""
        return [3]
    
    def _get_query_text(self):
        """Query text for height and plinth extraction."""
        return "Give height and plinth level as JSON"
    
    def _process_extracted_data(self, data_dict):
        """Process extracted data for height and plinth."""
        # Ensure values are in list format as expected by validation system
        def ensure_list(value):
            if value is None:
                return ["absent"]
            elif isinstance(value, list):
                return value
            else:
                return [value]
        
        return {
            "height": ensure_list(data_dict.get('height')),
            "plinth level": ensure_list(data_dict.get('plinth level'))
        }
    
    def _format_final_output(self, results):
        """Format final output for height and plinth extraction."""
        return results  # Results are already in correct dict format
